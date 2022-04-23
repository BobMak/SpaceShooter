import json
import os
import time
import cv2
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import numpy as np
import streamlit as st
import streamlit.components.v1 as components

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import Core.State as State
from Core import Mechanics

# removing white space
st.markdown(
            f'''
            <style>
                .reportview-container .sidebar-content {{
                    padding: 3px;
                    margins: 0px;
                }}
                .reportview-container .main .block-container {{
                    padding-top: {1}rem;
                }}
            </style>
            ''',unsafe_allow_html=True)

st.title("CA Animation Editor")

st.sidebar.title("CA Parameters")

# state
json_path = os.path.join("animation.json")
if 'animation_data' not in st.session_state:
    # try loading last saved animation parameters
    try:
        with open(json_path, "r") as f:
            animation_data = json.load(f)
        assert "diameter" in animation_data
    # default parameters
    except:
        animation_data = {
            "diameter": 50,
            "n_frames": 50,
            "i_red": 255,
            "i_green": 255,
            "i_blue": 255,
            "d_red": 5,
            "d_green": 5,
            "d_blue": 5,
            "spawn_threshold": 200,
            "spawn_threshold_count": 3,
        }
    st.session_state['animation_data'] = animation_data
    ad = animation_data
else:
    ad = st.session_state['animation_data']

diameter = st.sidebar.slider("Diameter", 1, 100, ad['diameter'])
n_frames = st.sidebar.slider("Frame Number", 1, 100, ad['n_frames'])

# first spawned cell colors
i_red = st.sidebar.slider("Initial Red", 0, 255, ad['i_red'])
i_green = st.sidebar.slider("Initial Green", 0, 255, ad['i_green'])
i_blue = st.sidebar.slider("Initial Blue", 0, 255, ad['i_blue'])

# color frame update
d_red = st.sidebar.slider("Red", 0, 30, ad['d_red'])
d_green = st.sidebar.slider("Green", 0, 30, ad['d_green'])
d_blue = st.sidebar.slider("Blue", 0, 30, ad['d_blue'])

# new cell spawn parameters
spawn_threshold = st.sidebar.slider("Spawn Threshold", 0, 254, ad['spawn_threshold'])
spawn_threshold_count = st.sidebar.slider("Spawn Threshold Count", 1, 8, ad['spawn_threshold_count'])

video_src_path = os.path.join("animation.html")


def redraw():
    f = open(video_src_path, "rb")
    video_src = f.read()
    components.html(video_src, height=1000, width=1000)

if os.path.exists(video_src_path):
    redraw()

def re_generate():
    a = Mechanics.Animation.generateExplosionAnimation(
        diameter,
        n_frames,
        (d_red, d_green, d_blue),
        (i_red, i_green, i_blue),
        spawn_threshold, spawn_threshold_count,
        numpy_out=True
    )

    # convert the animation into matplotlib animation
    fig = plt.figure()
    ims = []
    for frame in a:
        im = plt.imshow(frame, animated=True)
        ims.append([im])
    ani = animation.ArtistAnimation(fig, ims, interval=50, blit=True, repeat_delay=1000)

    # save as a html animation video file
    with open(video_src_path, "w") as ab:
        print(ani.to_html5_video(), file=ab)

    # save parameters
    ad = {
        "diameter": diameter,
        "n_frames": n_frames,
        "i_red": i_red,
        "i_green": i_green,
        "i_blue": i_blue,
        "d_red": d_red,
        "d_green": d_green,
        "d_blue": d_blue,
        "spawn_threshold": spawn_threshold,
        "spawn_threshold_count": spawn_threshold_count,
    }
    with open(os.path.join(json_path), "w") as f1:
        json.dump(ad, f1)

    # st.session_state['animation'] = True
    redraw()
    st.write("Animation generated")

generate = st.sidebar.button("Generate", on_click=re_generate)

