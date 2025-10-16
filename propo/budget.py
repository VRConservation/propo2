import reflex as rx
from .propo import ProposalState

def render_budget_item(item: rx.Var[dict]) -> rx.Component:
    """Render a single budget item"""
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.text(item["name"], font_weight="bold", color="white"),
                rx.text("Sub-task", font_size="sm", color="gray.400"),
                spacing="1",
                flex="1",
            ),
            rx.vstack(
                rx.text(f"${item['cost_per_unit']:.2f}/unit", color="green.300"),
                rx.text(f"{item['units']} units", color="gray.300"),
                spacing="1",
                align="end",
            ),
            rx.vstack(
                rx.text(f"${item['total_cost']:.2f}", font_weight="bold", color="green.400", font_size="lg"),
                rx.icon_button(
                    "trash",
                    color_scheme="red",
                    variant="soft",
                    size="1",
                    on_click=lambda: ProposalState.remove_budget_item(item["id"]),
                ),
                spacing="1",
                align="end",
            ),
            align="center",
            width="100%",
        ),
        background_color="gray.800",
        padding="3",
        width="100%",
    )

def task_selector() -> rx.Component:
    """Task selector component"""
    return rx.vstack(
        rx.text("Select Task:", color="white"),
        rx.cond(
            ProposalState.tasks.length() > 0,
            rx.vstack(
                rx.foreach(
                    ProposalState.tasks,
                    lambda task: rx.button(
                        task["name"],
                        variant=rx.cond(
                            ProposalState.selected_task_id == task["id"],
                            "solid",
                            "soft"
                        ),
                        background_color=rx.cond(
                            ProposalState.selected_task_id == task["id"],
                            "blue.600",
                            "gray.700"
                        ),
                        color="white",
                        width="100%",
                        on_click=lambda task_id=task["id"]: ProposalState.set_selected_task_id(task_id),
                    ),
                ),
                spacing="1",
                width="100%",
            ),
            rx.text("No tasks available", color="gray.400"),
        ),
        spacing="1",
        width="100%",
    )

def budget_input_section() -> rx.Component:
    """Input section for adding budget items"""
    return rx.card(
        rx.vstack(
            rx.heading("Add Budget Item", size="4", color="white"),
            
            # Task Selection
            task_selector(),
            
            # Sub-task Name
            rx.vstack(
                rx.text("Sub-task Name:", color="white"),
                rx.input(
                    placeholder="Enter sub-task name...",
                    value=ProposalState.new_subtask_name,
                    on_change=ProposalState.set_new_subtask_name,
                    width="100%",
                    background_color="gray.800",
                    color="white",
                    border_color="gray.600",
                ),
                spacing="1",
                width="100%",
            ),
            
            # Cost and Units
            rx.hstack(
                rx.vstack(
                    rx.text("Cost per Unit ($):", color="white"),
                    rx.input(
                        type_="number",
                        value=ProposalState.new_cost_per_unit,
                        on_change=ProposalState.set_new_cost_per_unit,
                        min_="0",
                        step="0.01",
                        background_color="gray.800",
                        color="white",
                        border_color="gray.600",
                    ),
                    spacing="1",
                    flex="1",
                ),
                rx.vstack(
                    rx.text("Units:", color="white"),
                    rx.input(
                        type_="number",
                        value=ProposalState.new_units,
                        on_change=ProposalState.set_new_units,
                        min_="0",
                        step="0.1",
                        background_color="gray.800",
                        color="white",
                        border_color="gray.600",
                    ),
                    spacing="1",
                    flex="1",
                ),
                spacing="3",
                width="100%",
            ),
            
            # Total Preview
            rx.text(
                f"Total: ${ProposalState.new_cost_per_unit * ProposalState.new_units:.2f}",
                font_weight="bold",
                color="green.400",
                font_size="lg",
            ),
            
            # Add Button
            rx.button(
                "Add Budget Item",
                background_color="green.600",
                color="white",
                _hover={"background_color": "green.500"},
                on_click=ProposalState.add_budget_item,
                width="100%",
                disabled=rx.cond(ProposalState.selected_task_id == "", True, False),
            ),
            
            spacing="3",
            width="100%",
        ),
        background_color="gray.900",
        padding="4",
        width="100%",
    )

def budget_summary_section() -> rx.Component:
    """Budget summary with total"""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("Budget Summary", size="4", color="white"),
                rx.text(
                    f"Total: ${ProposalState.total_budget:.2f}",
                    font_size="xl",
                    font_weight="bold",
                    color="green.400",
                ),
                justify="between",
                align="center",
                width="100%",
            ),
            rx.vstack(
                rx.cond(
                    ProposalState.budget_items.length() > 0,
                    rx.foreach(ProposalState.budget_items, render_budget_item),
                    rx.text("No budget items added yet.", color="gray.400", text_align="center"),
                ),
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

def budget_page() -> rx.Component:
    """Budget page with cost calculations"""
    return rx.vstack(
        rx.heading("Budget", size="6", color="white", margin_bottom="4"),
        
        rx.cond(
            ProposalState.tasks.length() > 0,
            rx.vstack(
                budget_input_section(),
                budget_summary_section(),
                spacing="4",
                width="100%",
            ),
            rx.card(
                rx.vstack(
                    rx.text("No tasks available", font_weight="bold", color="orange.400"),
                    rx.text("Please add tasks in the SOW section first.", color="gray.400"),
                    spacing="2",
                ),
                background_color="orange.100",
                border_color="orange.400",
                padding="4",
                width="100%",
            ),
        ),
        
        spacing="4",
        width="100%",
    )