"""Streamlit dashboard for HeatIndex."""
# TODO: add unit tests

from __future__ import annotations

import logging
import threading
import time
from collections import deque
from typing import Deque, Tuple

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Dashboard:
    """Streamlit UI running in same process."""

    def __init__(self) -> None:
        """Initialize dashboard buffers. # TODO: unit test"""
        self._buffer: Deque[Tuple[float, float, float]] = deque(maxlen=60)
        self._lock = threading.Lock()

    def push(self, clap: float, engage: float, heat: float) -> None:
        """Add metrics to internal buffer. # TODO: unit test"""
        with self._lock:
            self._buffer.append((clap, engage, heat))

    def start(self) -> None:
        """Start Streamlit interface. # TODO: unit test"""
        st.set_page_config(
            page_title="HeatIndex – Live Engagement",
            page_icon="🔥",
            layout="wide",
        )
        st.title("HeatIndex – Live Engagement")
        st.markdown(
            "- Monitor audience reaction in real time using webcam and microphone\n"
            "- Green circle means high engagement\n"
            "- ClapScore and FacialEngageIdx update every second",
        )
        if "data" not in st.session_state:
            st.session_state.data = deque(maxlen=60)
        placeholder = st.empty()
        while True:
            if self._buffer:
                with self._lock:
                    values = list(self._buffer)
                st.session_state.data = deque(values, maxlen=60)
                clap, engage, heat = values[-1]
                with placeholder.container():
                    st.subheader("Metrics")
                    col1, col2, col3 = st.columns(3)
                    df = pd.DataFrame(
                        st.session_state.data,
                        columns=["clap", "engage", "heat"],
                    )
                    last10 = df.tail(10)
                    delta_clap = clap - last10["clap"].mean() if not last10.empty else 0
                    delta_face = (
                        engage - last10["engage"].mean() if not last10.empty else 0
                    )
                    delta_heat = heat - last10["heat"].mean() if not last10.empty else 0
                    col1.metric("ClapScore", f"{clap:.1f}", f"{delta_clap:+.1f}")
                    col2.metric(
                        "FacialEngageIdx",
                        f"{engage:.1f}",
                        f"{delta_face:+.1f}",
                    )
                    col3.metric("HeatIndex", f"{heat:.1f}", f"{delta_heat:+.1f}")
                st.line_chart(df)
                color = "green" if heat >= 70 else "yellow" if heat >= 40 else "red"
                st.markdown(
                    (
                        f"<div style='width:30px;height:30px;border-radius:50%;"
                        f"background:{color};margin:auto'></div>"
                    ),
                    unsafe_allow_html=True,
                )
            time.sleep(1)
