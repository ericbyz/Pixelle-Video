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
Standard Pipeline UI

Implements the progressive tab layout for the Standard Pipeline.
"""

import streamlit as st
from typing import Any
from web.i18n import tr

from web.pipelines.base import PipelineUI, register_pipeline_ui

# Import components
from web.components.content_input import render_content_input, render_bgm_section, render_version_info
from web.components.style_config import render_style_config
from web.components.output_preview import render_output_preview
from web.components.progressive_tabs import render_step_selector, render_step_workspace


class StandardPipelineUI(PipelineUI):
    """
    UI for the Standard Video Generation Pipeline.
    Implements a progressive script -> style -> generate flow.
    """
    name = "quick_create"
    icon = "⚡"
    
    @property
    def display_name(self):
        return tr("pipeline.quick_create.name")
    
    @property
    def description(self):
        return tr("pipeline.quick_create.description")
    
    def render(self, pixelle_video: Any):
        steps = [
            tr("progressive.step.content"),
            tr("progressive.step.style"),
            tr("progressive.step.generate"),
        ]
        step_key = f"{self.name}_progressive_step"
        params_key = f"{self.name}_progressive_params"
        active_step = render_step_selector(steps, step_key)
        params = st.session_state.setdefault(params_key, {})

        with render_step_workspace():
            # ====================================================================
            # Step 1: Content Input & BGM
            # ====================================================================
            if active_step == 0:
                main_col, side_col = st.columns([2, 1])

                # Content input (mode, text, title, n_scenes)
                with main_col:
                    content_params = render_content_input()

                # BGM selection (bgm_path, bgm_volume)
                with side_col:
                    bgm_params = render_bgm_section()
                    render_version_info()

                params.update({
                    **content_params,
                    **bgm_params,
                })

            # ====================================================================
            # Step 2: Style Configuration
            # ====================================================================
            elif active_step == 1:
                # Style configuration (TTS, template, workflow, etc.)
                style_params = render_style_config(pixelle_video)
                params.update(style_params)

            # ====================================================================
            # Step 3: Output Preview
            # ====================================================================
            else:
                # Combine all parameters
                video_params = {
                    "pipeline": self.name,
                    **params,
                }

                # Render output preview (generate button, progress, video preview)
                render_output_preview(pixelle_video, video_params)


# Register self
register_pipeline_ui(StandardPipelineUI)
