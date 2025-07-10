"""Streamlit dashboard for Heat Index."""
# TODO: add unit tests

from __future__ import annotations

import logging
import threading
import time
from collections import deque
from typing import Deque, Dict, Tuple

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Dashboard:
    """Streamlit UI running in the same process."""

    def __init__(self) -> None:
        """Initialize buffers."""  # TODO unit-test
        self._buffer: Deque[Tuple[float, float, float, Dict[str, float]]] = deque(maxlen=60)
        self._lock = threading.Lock()

    def push(self, engage: float, focus: float, heat: float, demo: Dict[str, float]) -> None:
        """Add metrics to internal buffer."""  # TODO unit-test
        with self._lock:
            self._buffer.append((engage, focus, heat, demo))

    def start(self) -> None:
        """Start Streamlit interface."""  # TODO unit-test
        st.set_page_config(
            page_title="Heat Index — Live Engagement Analytics",
            page_icon="🔥",
            layout="wide",
        )
        st.title("Heat Index — Live Engagement Analytics")
        st.markdown(
            "- No video frames are stored. All processing is local.\n"
            "- Age and gender are rough estimates."
        )
        if "data" not in st.session_state:
            st.session_state.data = deque(maxlen=60)
        placeholder = st.empty()
        while True:
            demo_toggle = st.sidebar.checkbox("Demographics ON", True, key="demo")
            if self._buffer:
                with self._lock:
                    values = list(self._buffer)
                st.session_state.data = deque(values, maxlen=60)
                engage, focus, heat, demo = values[-1]
                df = pd.DataFrame(
                    [v[:3] for v in st.session_state.data],
                    columns=["engage", "focus", "heat"],
                )
                last10 = df.tail(10)
                delta_e = engage - last10["engage"].mean() if not last10.empty else 0
                delta_f = focus - last10["focus"].mean() if not last10.empty else 0
                delta_h = heat - last10["heat"].mean() if not last10.empty else 0
                with placeholder.container():
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Engage %", f"{engage:.1f}", f"{delta_e:+.1f}")
                    col2.metric("Focus %", f"{focus:.1f}", f"{delta_f:+.1f}")
                    col3.metric("Heat Index", f"{heat:.1f}", f"{delta_h:+.1f}")
                    st.line_chart(df)
                    color = "green" if heat >= 70 else "yellow" if heat >= 40 else "red"
                    st.markdown(
                        f"<div style='width:30px;height:30px;border-radius:50%;background:{color};margin:auto'></div>",
                        unsafe_allow_html=True,
                    )
                    if demo_toggle:
                        pie_df = pd.DataFrame(
                            {
                                "label": ["male", "female", "unknown"],
                                "value": [demo["male"], demo["female"], demo["unknown"]],
                            }
                        )
                        st.plotly_chart(
                            {
                                "data": [
                                    {
                                        "values": pie_df["value"],
                                        "labels": pie_df["label"],
                                        "type": "pie",
                                    }
                                ],
                                "layout": {"title": "Gender"},
                            }
                        )
                        age_df = pd.DataFrame(
                            {
                                "age": ["teen", "twenties", "thirties", "forties"],
                                "val": [demo["teen"], demo["twenties"], demo["thirties"], demo["forties"]],
                            }
                        )
                        st.bar_chart(age_df.set_index("age"))
            time.sleep(1)
