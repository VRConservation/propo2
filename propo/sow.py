import reflex as rx
from .propo import ProposalState

def render_task_item(task: rx.Var[dict]) -> rx.Component:
    """Render a single task item with edit capability"""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(task["name"], font_weight="bold", color="white", flex="1"),
                rx.icon_button(
                    "trash",
                    color_scheme="red",
                    variant="soft",
                    size="1",
                    on_click=lambda: ProposalState.remove_task(task["id"]),
                ),
                align="center",
                width="100%",
            ),
            rx.text_area(
                placeholder="Task description...",
                value=task["description"],
                on_change=lambda value: ProposalState.update_task_description(task["id"], value),
                width="100%",
                background_color="gray.800",
                color="white",
                border_color="gray.600",
                rows="3",
            ),
            spacing="2",
            width="100%",
        ),
        background_color="gray.800",
        padding="3",
        width="100%",
    )

def task_input_section() -> rx.Component:
    """Input section for adding new tasks"""
    return rx.card(
        rx.vstack(
            rx.heading("Tasks", size="4", color="white"),
            rx.hstack(
                rx.input(
                    placeholder="Enter task name...",
                    value=ProposalState.new_task_name,
                    on_change=ProposalState.set_new_task_name,
                    flex="1",
                    background_color="gray.800",
                    color="white",
                    border_color="gray.600",
                ),
                rx.button(
                    "Add Task",
                    background_color="blue.600",
                    color="white",
                    _hover={"background_color": "blue.500"},
                    on_click=ProposalState.add_task,
                ),
                spacing="2",
                width="100%",
            ),
            rx.vstack(
                rx.foreach(ProposalState.tasks, render_task_item),
                spacing="2",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        background_color="gray.900",
        padding="4",
        width="100%",
    )

def sow_page() -> rx.Component:
    """Statement of Work page"""
    return rx.vstack(
        rx.heading("Statement of Work", size="6", color="white", margin_bottom="4"),
        
        # Project Summary Section
        rx.card(
            rx.vstack(
                rx.heading("Project Summary", size="4", color="white"),
                rx.text_area(
                    placeholder="Enter project summary and scope...",
                    value=ProposalState.project_summary,
                    on_change=ProposalState.set_project_summary,
                    width="100%",
                    rows="5",
                    background_color="gray.800",
                    color="white",
                    border_color="gray.600",
                ),
                spacing="2",
                width="100%",
            ),
            background_color="gray.900",
            padding="4",
            width="100%",
        ),
        
        # Tasks Section
        task_input_section(),
        
        # Qualifications Section
        rx.card(
            rx.vstack(
                rx.heading("Qualifications", size="4", color="white"),
                rx.text_area(
                    placeholder="Enter team qualifications and relevant experience...",
                    value=ProposalState.qualifications,
                    on_change=ProposalState.set_qualifications,
                    width="100%",
                    rows="5",
                    background_color="gray.800",
                    color="white",
                    border_color="gray.600",
                ),
                spacing="2",
                width="100%",
            ),
            background_color="gray.900",
            padding="4",
            width="100%",
        ),
        
        spacing="4",
        width="100%",
    )