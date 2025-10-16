import reflex as rx
from .propo import ProposalState
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

class TimelineInputState(rx.State):
    """Local state for timeline inputs"""
    task_lead_months: dict = {}
    task_duration_months: dict = {}
    
    @rx.event
    def set_task_lead(self, task_id: str, value: str):
        try:
            self.task_lead_months[task_id] = int(value) if value else 0
        except ValueError:
            self.task_lead_months[task_id] = 0
            
    @rx.event
    def set_task_duration(self, task_id: str, value: str):
        try:
            self.task_duration_months[task_id] = int(value) if value else 1
        except ValueError:
            self.task_duration_months[task_id] = 1
            
    @rx.event
    def save_timeline_item(self, task_id: str):
        lead = self.task_lead_months.get(task_id, 0)
        duration = self.task_duration_months.get(task_id, 1)
        ProposalState.add_timeline_item(task_id, lead, duration)

def generate_timeline_header(start_date_str: str, total_months: int) -> rx.Component:
    """Generate the timeline header with quarters and years"""
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    except:
        start_date = date.today()
    
    headers = []
    current_date = start_date
    
    for i in range(total_months):
        month_year = current_date.strftime("%b %Y")
        quarter = f"Q{((current_date.month - 1) // 3) + 1}"
        
        headers.append(
            rx.vstack(
                rx.text(quarter, font_size="xs", color="gray.400"),
                rx.text(month_year, font_size="xs", color="white", font_weight="bold"),
                spacing="1",
                align="center",
                min_width="80px",
                padding="1",
            )
        )
        current_date += relativedelta(months=1)
    
    return rx.hstack(*headers, spacing="1", overflow_x="auto")

def render_gantt_bar(task: rx.Var[dict], timeline_item: dict) -> rx.Component:
    """Render a Gantt chart bar for a task"""
    lead_months = timeline_item.get("lead_months", 0)
    duration_months = timeline_item.get("duration_months", 1)
    
    # Create empty cells for lead time
    lead_cells = [
        rx.box(min_width="80px", height="20px", margin="1")
        for _ in range(lead_months)
    ]
    
    # Create filled cells for task duration
    duration_cells = [
        rx.box(
            background_color="blue.500",
            min_width="80px", 
            height="20px",
            margin="1",
            border_radius="2px",
        )
        for _ in range(duration_months)
    ]
    
    return rx.hstack(
        rx.text(
            task["name"],
            min_width="200px",
            color="white",
            font_weight="bold",
            padding_right="4",
        ),
        *lead_cells,
        *duration_cells,
        spacing="0",
        align="center",
    )

def task_timeline_input(task: rx.Var[dict]) -> rx.Component:
    """Input section for a single task's timeline"""
    return rx.card(
        rx.vstack(
            rx.text(task["name"], font_weight="bold", color="white"),
            rx.hstack(
                rx.vstack(
                    rx.text("Lead Time (months):", color="white", font_size="sm"),
                    rx.input(
                        type_="number",
                        value=TimelineInputState.task_lead_months.get(task["id"], 0),
                        on_change=lambda value: TimelineInputState.set_task_lead(task["id"], value),
                        min_="0",
                        max_="24",
                        width="100px",
                        background_color="gray.800",
                        color="white",
                        border_color="gray.600",
                    ),
                    spacing="1",
                ),
                rx.vstack(
                    rx.text("Duration (months):", color="white", font_size="sm"),
                    rx.input(
                        type_="number",
                        value=TimelineInputState.task_duration_months.get(task["id"], 1),
                        on_change=lambda value: TimelineInputState.set_task_duration(task["id"], value),
                        min_="1",
                        max_="24",
                        width="100px",
                        background_color="gray.800",
                        color="white",
                        border_color="gray.600",
                    ),
                    spacing="1",
                ),
                rx.button(
                    "Update",
                    background_color="blue.600",
                    color="white",
                    _hover={"background_color": "blue.500"},
                    on_click=lambda: TimelineInputState.save_timeline_item(task["id"]),
                    size="2",
                ),
                spacing="3",
                align="end",
            ),
            spacing="2",
            width="100%",
        ),
        background_color="gray.800",
        padding="3",
        width="100%",
    )

def timeline_input_section() -> rx.Component:
    """Input section for timeline settings"""
    return rx.card(
        rx.vstack(
            rx.heading("Timeline Settings", size="4", color="white"),
            rx.vstack(
                rx.text("Project Start Date:", color="white"),
                rx.input(
                    type_="date",
                    value=ProposalState.start_date,
                    on_change=ProposalState.set_start_date,
                    background_color="gray.800",
                    color="white",
                    border_color="gray.600",
                ),
                spacing="1",
                width="200px",
            ),
            rx.text("Task Timeline Setup:", color="white", font_weight="bold", margin_top="4"),
            rx.vstack(
                rx.foreach(ProposalState.tasks, task_timeline_input),
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

def gantt_chart_section() -> rx.Component:
    """Gantt chart visualization"""
    # Calculate total months needed
    max_months = 12  # Default minimum
    for timeline_item in ProposalState.timeline_items:
        total = timeline_item.get("lead_months", 0) + timeline_item.get("duration_months", 1)
        max_months = max(max_months, total)
    
    return rx.card(
        rx.vstack(
            rx.heading("Gantt Chart", size="4", color="white"),
            rx.cond(
                ProposalState.timeline_items.length() > 0,
                rx.vstack(
                    # Timeline header
                    rx.hstack(
                        rx.box(min_width="200px"),  # Space for task names
                        generate_timeline_header(ProposalState.start_date, max_months),
                        spacing="0",
                        overflow_x="auto",
                        width="100%",
                    ),
                    # Task bars
                    rx.foreach(
                        ProposalState.tasks.filter(
                            lambda task: ProposalState.timeline_items.filter(
                                lambda t: t["task_id"] == task["id"]
                            ).length() > 0
                        ).map(
                            lambda task: {
                                **task,
                                "timeline": ProposalState.timeline_items.filter(
                                    lambda t: t["task_id"] == task["id"]
                                )[0]
                            }
                        ),
                        lambda task_with_timeline: render_gantt_bar(
                            task_with_timeline, 
                            task_with_timeline["timeline"]
                        ),
                    ),
                    spacing="2",
                    width="100%",
                    overflow_x="auto",
                ),
                rx.text("No timeline items configured yet.", color="gray.400", text_align="center"),
            ),
            spacing="3",
            width="100%",
        ),
        background_color="gray.900",
        padding="4",
        width="100%",
    )

def timeline_page() -> rx.Component:
    """Timeline/Gantt chart page"""
    return rx.vstack(
        rx.heading("Timeline", size="6", color="white", margin_bottom="4"),
        
        rx.cond(
            ProposalState.tasks.length() > 0,
            rx.vstack(
                timeline_input_section(),
                gantt_chart_section(),
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