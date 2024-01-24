import matplotlib
import streamlit as st
from streamlit_folium import folium_static
import folium
import branca.colormap
import numpy as np
import pandas as pd
from typing import List
from humanfriendly import parse_size, format_size
from typing import Tuple, List


def find_column(df: pd.DataFrame, possible_column_names: List[str]) -> str:
    matches = [x for x in df.columns if x in possible_column_names]
    if not len(matches):
        return None
    elif len(matches) == 1:
        return matches[0]
    else:
        raise Exception(
            f"more than one column of df with columns={df.columns} match query list {possible_column_names}")


def get_durations(data: pd.DataFrame):
    if "receive_time" in data.columns and "send_time" in data.columns:
        return list(data["receive_time"] - data["send_time"])
    elif "duration" in data.columns:
        return list(data["duration"])
    else:
        raise Exception("Didn't find columns for the duration!")


def get_sizes(df):
    return list(df[find_column(df, ["packet_size", "size", "sizes"])])


def process_dfs(dfs):
    if not dfs:
        return [], [], []
    sizes = sum([list(get_sizes(df)) for df in dfs], [])
    ys = sum([list(df[find_column(df, ["y", "Y"])]) for df in dfs], [])
    xs = sum([list(df[find_column(df, ["x", "X"])]) for df in dfs], [])
    durations = sum([get_durations(df) for df in dfs], [])
    latencies = [size / t for size, t in zip(sizes, durations)]

    with st.expander("Options"):
        options = [format_size(x) for x in sorted(set(sizes))]
        min_size, max_size = map(parse_size, st.select_slider("Packet Size",
                                                              options=options,
                                                              value=[options[0], options[-1]]))
        if st.checkbox("Reverse X and Y", value=False):
            _t = xs
            xs = ys
            ys = _t

    df = pd.DataFrame({"size": sizes, "y": ys, "x": xs,
                      "duration": durations,
                       "latency": latencies})
    df = df[df["size"] <= max_size]
    df = df[df["size"] >= min_size]

    st.write(f"Min: {min(df['latency'])}")
    st.write(f"Max: {max(df['latency'])}")

    with st.expander("Selected Data Points"):
        print_df = pd.DataFrame({
            "y": df["y"],
            "x": df["x"],
            "Packet Size": df["size"].map(format_size),
            "Duration": df["duration"],
            "Bytes per Second": df["latency"].map(format_size)
        })
        st.write(print_df)

    d = dict()
    for _, row in df.iterrows():
        pos = (row["y"], row["x"])
        d[pos] = d.get(pos, []) + [row["latency"]]

    items = d.items()
    ys = [i[0][0] for i in items]
    xs = [i[0][1] for i in items]
    latencies = [np.average(i[1]) for i in items]

    with st.expander("Final data points (the average at each position):"):
        print_df = pd.DataFrame(
            {"y": ys, "x": xs, "Average Bytes per Second": map(format_size, latencies)})
        st.write(print_df)

    st.write(f"Min per Point: {min(latencies)}")
    st.write(f"Max per Point: {max(latencies)}")

    return ys, xs, latencies


def draw_map(ys: list, xs: list, latencies: list):
    option = st.selectbox('Type of map to generate:',
                          ('None', 'folium', 'scatter', 'interpolate', "contour"))
    if len(latencies):
        if option == "folium":
            draw_map_folium(ys, xs, latencies)
        elif option in ["scatter", "interpolate"]:
            draw_map_pyplot(ys, xs, latencies, option)
        elif option == "contour":
            draw_map_contour(ys, xs, latencies)
        elif option == 'None':
            st.write("No Map Type selected!")
        else:
            raise NotImplementedError()
    else:
        st.write("No data!")


def interpolate(ys, xs, latencies):
    import numpy as np
    from scipy.interpolate import griddata
    with st.expander("Interpolation Options:"):
        resolution = st.number_input("Resolution (in cm):", value=10)
        interpolation_option = st.selectbox(
            'scipy interpolation type:', ('cubic', 'nearest', 'linear'))
    grid_y, grid_x = np.mgrid[min(ys):max(
        ys)+1:resolution, min(xs):max(xs)+1:resolution]
    grid_z = griddata(list(zip(ys, xs)), latencies,
                      (grid_y, grid_x), method=interpolation_option)
    return grid_y, grid_x, grid_z


def draw_map_contour(ys, xs, latencies):
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")
    Y, X, Z = interpolate(ys, xs, latencies)
    plotted = ax.plot_surface(Y, X, Z, rstride=1, cstride=1,
                              cmap='viridis', edgecolor='none')
    ax.set_box_aspect((np.ptp(ys), np.ptp(xs), max(np.ptp(xs), np.ptp(ys))))
    fig.colorbar(plotted, label="Bytes per Second")
    z1, z2 = ax.get_zlim()
    z1 = st.number_input("z1:", value=z1)
    z2 = st.number_input("z2:", value=z2)
    if st.checkbox("Invert yaxis"):
        ax.set_ylim(ax.get_ylim()[::-1])
    if st.checkbox("Invert xaxis:"):
        ax.set_xlim(ax.get_xlim()[::-1])
    ax.set_zlim((z1, z2))

    st.pyplot(fig)


def draw_map_pyplot(ys: list, xs: list, latencies: list, plottype="scatter"):
    assert plottype in ["scatter", "interpolate"]
    st.subheader("Matplotlib")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()

    st.write(
        "Matplotlib colormap to be used. See [the documentation](https://matplotlib.org/stable/tutorials/colors/colormaps.html) for details. Append _r to a colormap's name to reverse it.")
    cmap = st.text_input("colormap", value="hot")  # previously: viridis
    unit = st.text_input("Unit", value="cm")
    name = st.text_input("Plot Title:")
    if st.checkbox("Show Grid", value=False):
        ax.grid(True)
    dx = max(xs) - min(xs)
    dy = max(ys) - min(ys)

    with st.expander("Other Options:"):
        xmin = st.number_input("xmin:", value=min(xs) - 0.05 * dx)
        xmax = st.number_input("xmax:", value=max(xs) + 0.05 * dx)
        ymin = st.number_input("ymin:", value=min(ys) - 0.05 * dy)
        ymax = st.number_input("ymax:", value=max(ys) + 0.05 * dy)
        vmin = st.number_input("vmin:", value=min(latencies))
        vmax = st.number_input("vmax:", value=max(latencies))

    if plottype == "scatter":
        plotted = ax.scatter(xs, ys, c=latencies,
                             vmin=vmin, vmax=vmax,
                             label=latencies, cmap=plt.get_cmap(cmap))
    elif plottype == "interpolate":
        from scipy.interpolate import griddata
        ly, uy = min(ys), max(ys) + 1
        lx, ux = min(xs), max(xs) + 1
        # grid_y, grid_x = np.mgrid[ly:uy:resolution, lx:ux:resolution]
        # grid_z0 = griddata(list(zip(ys, xs)), latencies, (grid_y, grid_x),
        #                    method=interpolation_option)
        Y, X, Z = interpolate(ys, xs, latencies)
        fig, ax = plt.subplots()
        plotted = ax.imshow(Z, origin='lower',
                            vmin=vmin, vmax=vmax,
                            cmap=plt.get_cmap(
                                cmap), extent=(lx, ux, ly, uy))
    else:
        raise Exception("Invalid type")
    fig.colorbar(plotted, label="Bytes per Second")

    ax.set_xlabel(f"Y Position in {unit}")
    ax.set_ylabel(f"X Position in {unit}")
    ax.axis("equal")

    ax.set_xlim([xmin, xmax])
    ax.set_ylim([ymin, ymax])
    ax.set_title(label=name)

    st.pyplot(fig)


def draw_map_folium(ys: list, xs: list, latencies: list):
    if len(ys) == 0:
        return None
    circle_radius = st.slider("Circle Radius", 0.1, 10.0, 1.0)
    m = folium.Map(max_zoom=19)  # 19 is max zoom level with map tiles

    colormap = branca.colormap.linear.RdYlBu_08.scale(np.quantile(latencies, 0.05),
                                                      np.quantile(latencies, 0.95))
    colormap.add_to(m)
    positions = []
    for latency, y, x in zip(latencies, ys, xs):
        c = "black" if (latency < 1e-3) else colormap(latency)
        pos = (y, x)
        positions.append(pos)

        m.add_child(folium.Circle(
            location=pos,
            radius=circle_radius,
            color=c,
            fill_color=c,
            fill_opacity=1.0))
    m.fit_bounds(positions)

    folium_static(m, width=1000, height=700)


def main():
    st.set_page_config(layout="wide")
    st.title("Latency Map")
    st.header("Load Files")
    uploaded_files = st.file_uploader("Choose CSV files", type=[
        'csv'], accept_multiple_files=True)
    if uploaded_files is not None:
        dfs = []
        for file in uploaded_files:
            df = pd.read_csv(file)
            dfs.append(df)
            with st.expander(file.name):
                st.write(df)

        st.header("Process Data")
        ys, xs, latencies = process_dfs(dfs)

        st.header("Create Map")
        draw_map(ys, xs, latencies)


if __name__ == "__main__":
    main()
