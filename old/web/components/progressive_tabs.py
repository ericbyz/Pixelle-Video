# Copyright (C) 2025 AIDC-AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Progressive selection helpers for Streamlit UI.
"""

from typing import Iterable, Sequence

import streamlit as st

from web.i18n import tr


def inject_progressive_tab_styles():
    """Apply styling for progressive workflows."""
    st.markdown(
        """
        <style>
            :root {
                --pv-accent: #ef4444;
                --pv-ink: #111827;
                --pv-muted: #6b7280;
                --pv-line: rgba(17, 24, 39, 0.10);
                --pv-panel: #ffffff;
                --pv-soft: #f8fafc;
            }

            .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
                max-width: 90rem;
            }

            /* Section containers spacing */
            [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
                gap: 0.25rem;
            }

            /* Container border styling */
            div[data-testid="stVerticalBlockBorderWrapper"] {
                padding: 1rem 1.25rem;
                border-radius: 0.75rem;
            }

            div[data-testid="stSegmentedControl"] {
                width: 100%;
            }

            div[data-testid="stSegmentedControl"] [role="group"] {
                width: 100%;
                display: flex;
                flex-wrap: nowrap;
                gap: 0.5rem;
            }

            div[data-testid="stSegmentedControl"] label {
                flex: 1 1 0;
                justify-content: center;
                min-width: 0;
                padding-left: 0.4rem;
                padding-right: 0.4rem;
            }

            div[data-testid="stSegmentedControl"] label p {
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
                font-size: 0.9rem;
            }

            .progressive-flow-title {
                color: var(--pv-ink);
                font-size: 1rem;
                font-weight: 700;
                line-height: 1.4;
                margin: 0.5rem 0 0.15rem;
            }

            .progressive-flow-copy {
                color: var(--pv-muted);
                font-size: 0.82rem;
                line-height: 1.45;
                margin-bottom: 0.4rem;
            }

            .progressive-step-caption {
                color: rgba(49, 51, 63, 0.68);
                font-size: 0.9rem;
                margin: 0.3rem 0 0.4rem 0;
                text-align: center;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_pipeline_selector(pipelines: Sequence, key: str = "progressive_pipeline_selector"):
    """Render the top-level pipeline selector and return the selected pipeline."""
    if not pipelines:
        return None

    pipeline_by_name = {pipeline.name: pipeline for pipeline in pipelines}
    options = list(pipeline_by_name.keys())
    current = st.session_state.get(key, options[0])
    default = current if current in pipeline_by_name else options[0]

    st.markdown(
        f"""
        <div class="progressive-flow-title">{tr('progressive.pipeline.title')}</div>
        <div class="progressive-flow-copy">{tr('progressive.pipeline.caption')}</div>
        """,
        unsafe_allow_html=True,
    )

    def format_pipeline(name: str) -> str:
        pipeline = pipeline_by_name[name]
        return f"{pipeline.icon} {pipeline.display_name}"

    selected_name = st.selectbox(
        tr("progressive.pipeline.select"),
        options=options,
        index=options.index(default),
        format_func=format_pipeline,
        key=key,
        label_visibility="collapsed",
        width="stretch",
    )

    if selected_name is None:
        selected_name = default

    return pipeline_by_name[selected_name]


def render_step_tabs(labels: Iterable[str]):
    """Create numbered tabs for step-by-step configuration."""
    return st.tabs([f"{index}. {label}" for index, label in enumerate(labels, start=1)])


def render_step_selector(labels: Sequence[str], key: str) -> int:
    """Render an in-page step selector and return the active step index."""
    if not labels:
        return 0

    options = list(range(len(labels)))
    if key not in st.session_state or st.session_state[key] not in options:
        st.session_state[key] = 0
    widget_key = f"{key}_selector"
    if st.session_state.get(widget_key) not in options:
        st.session_state[widget_key] = st.session_state[key]

    def format_step(index: int) -> str:
        return f"{index + 1}. {labels[index]}"

    if hasattr(st, "segmented_control"):
        selected = st.segmented_control(
            tr("progressive.step.select"),
            options=options,
            format_func=format_step,
            key=widget_key,
            label_visibility="collapsed",
            width="stretch",
        )
    else:
        selected = st.radio(
            tr("progressive.step.select"),
            options=options,
            index=st.session_state[key],
            format_func=format_step,
            key=widget_key,
            horizontal=True,
            label_visibility="collapsed",
        )

    if selected is None:
        selected = st.session_state[key]

    st.session_state[key] = selected
    return selected


def _set_step(state_key: str, widget_key: str, step: int):
    st.session_state[state_key] = step
    st.session_state[widget_key] = step


def render_step_navigation(labels: Sequence[str], key: str, divider: bool = False):
    """Render navigation controls close to the step selector."""
    if not labels:
        return

    current = st.session_state.get(key, 0)
    current = max(0, min(current, len(labels) - 1))
    widget_key = f"{key}_selector"

    if divider:
        st.markdown("---")

    prev_col, status_col, next_col = st.columns([1, 2.4, 1])

    with prev_col:
        st.button(
            tr("progressive.step.previous"),
            key=f"{key}_previous",
            use_container_width=True,
            disabled=current <= 0,
            on_click=_set_step,
            args=(key, widget_key, current - 1),
        )

    with status_col:
        st.caption(
            tr(
                "progressive.step.current",
                step=current + 1,
                total=len(labels),
                label=labels[current],
            )
        )

    with next_col:
        st.button(
            tr("progressive.step.next"),
            key=f"{key}_next",
            type="primary",
            use_container_width=True,
            disabled=current >= len(labels) - 1,
            on_click=_set_step,
            args=(key, widget_key, current + 1),
        )


def render_step_workspace():
    """Create a workspace container that adapts to content height."""
    return st.container(border=False)
