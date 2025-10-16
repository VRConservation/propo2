import uuid
import reflex as rx
from typing import Any, Dict, List, Optional
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

class ProposalState(rx.State):
    # Current tab
    current_tab: str = "sow"
    
    # SOW Data
    project_summary: str = ""
    qualifications: str = ""
    tasks: List[Dict[str, Any]] = []
    new_task_name: str = ""
    
    # Budget Data
    budget_items: List[Dict[str, Any]] = []
    new_subtask_name: str = ""
    new_cost_per_unit: float = 0.0
    new_units: float = 0.0
    selected_task_id: str = ""
    
    # Timeline Data
    start_date: str = datetime.now().strftime("%Y-%m-%d")
    timeline_items: List[Dict[str, Any]] = []

    # Computed properties
    @rx.var
    def total_budget(self) -> float:
        return sum(item.get("total_cost", 0) for item in self.budget_items)
    
    @rx.var
    def tasks_for_budget(self) -> List[Dict[str, str]]:
        return [{"id": task["id"], "name": task["name"]} for task in self.tasks]
    
    @rx.var
    def task_options(self) -> List[str]:
        return [task["name"] for task in self.tasks]

    # SOW Events
    @rx.event
    def set_project_summary(self, value: str):
        self.project_summary = value
    
    @rx.event
    def set_qualifications(self, value: str):
        self.qualifications = value
        
    @rx.event
    def set_new_task_name(self, value: str):
        self.new_task_name = value.strip()
        
    @rx.event
    def add_task(self):
        if not self.new_task_name:
            return
        task_id = str(uuid.uuid4())
        self.tasks.append({
            "id": task_id,
            "name": self.new_task_name,
            "description": ""
        })
        self.new_task_name = ""
        
    @rx.event
    def remove_task(self, task_id: str):
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        # Also remove related budget items and timeline items
        self.budget_items = [b for b in self.budget_items if b["task_id"] != task_id]
        self.timeline_items = [t for t in self.timeline_items if t["task_id"] != task_id]
        
    @rx.event
    def update_task_description(self, task_id: str, description: str):
        for task in self.tasks:
            if task["id"] == task_id:
                task["description"] = description
                break

    # Budget Events
    @rx.event
    def set_selected_task_id(self, task_id: str):
        self.selected_task_id = task_id
        
    @rx.event
    def set_new_subtask_name(self, value: str):
        self.new_subtask_name = value.strip()
        
    @rx.event
    def set_new_cost_per_unit(self, value: str):
        try:
            self.new_cost_per_unit = float(value) if value else 0.0
        except ValueError:
            self.new_cost_per_unit = 0.0
            
    @rx.event
    def set_new_units(self, value: str):
        try:
            self.new_units = float(value) if value else 0.0
        except ValueError:
            self.new_units = 0.0
            
    @rx.event
    def add_budget_item(self):
        if not self.new_subtask_name or not self.selected_task_id:
            return
        total_cost = self.new_cost_per_unit * self.new_units
        self.budget_items.append({
            "id": str(uuid.uuid4()),
            "task_id": self.selected_task_id,
            "name": self.new_subtask_name,
            "cost_per_unit": self.new_cost_per_unit,
            "units": self.new_units,
            "total_cost": total_cost
        })
        self.new_subtask_name = ""
        self.new_cost_per_unit = 0.0
        self.new_units = 0.0
        
    @rx.event
    def remove_budget_item(self, item_id: str):
        self.budget_items = [b for b in self.budget_items if b["id"] != item_id]

    # Timeline Events
    @rx.event
    def set_start_date(self, value: str):
        self.start_date = value
        
    @rx.event
    def add_timeline_item(self, task_id: str, lead_months: int, duration_months: int):
        # Remove existing timeline item for this task
        self.timeline_items = [t for t in self.timeline_items if t["task_id"] != task_id]
        
        # Add new timeline item
        self.timeline_items.append({
            "id": str(uuid.uuid4()),
            "task_id": task_id,
            "lead_months": lead_months,
            "duration_months": duration_months
        })
    
    # Navigation Events
    @rx.event
    def set_tab(self, tab_name: str):
        self.current_tab = tab_name

# Tab button component
def tab_button(tab_name: str, label: str, icon: str) -> rx.Component:
    return rx.button(
        rx.hstack(
            rx.icon(icon, size=16),
            rx.text(label),
            spacing="2",
            align="center",
        ),
        variant=rx.cond(ProposalState.current_tab == tab_name, "solid", "soft"),
        background_color=rx.cond(
            ProposalState.current_tab == tab_name, "blue.600", "gray.700"
        ),
        color="white",
        _hover={"background_color": rx.cond(
            ProposalState.current_tab == tab_name, "blue.500", "gray.600"
        )},
        on_click=lambda: ProposalState.set_tab(tab_name),
        size="3",
        width="150px",
    )

def navigation_bar() -> rx.Component:
    """Top navigation with tabs"""
    return rx.hstack(
        tab_button("sow", "SOW", "file-text"),
        tab_button("budget", "Budget", "dollar-sign"),
        tab_button("timeline", "Timeline", "calendar"),
        spacing="4",
        justify="center",
        padding="4",
        background_color="gray.800",
        border_radius="8px",
        width="100%",
    )

def main_content() -> rx.Component:
    """Main content area that switches between pages"""
    from .sow import sow_page
    from .budget import budget_page  
    from .timeline import timeline_page
    
    return rx.box(
        rx.cond(
            ProposalState.current_tab == "sow",
            sow_page(),
            rx.cond(
                ProposalState.current_tab == "budget",
                budget_page(),
                timeline_page(),
            ),
        ),
        width="100%",
    )

def index() -> rx.Component:
    return rx.center(
        rx.card(
            rx.vstack(
                rx.heading("Proposal Generator", size="7", color="white", text_align="center"),
                navigation_bar(),
                rx.separator(border_color="gray.700"),
                main_content(),
                width="min(1200px, 95vw)",
                spacing="6",
            ),
            size="4",
            width="min(1240px, 98vw)",
            shadow="lg",
            background_color="gray.900",
        ),
        min_h="100vh",
        padding_y="8",
        background_color="black",
    )

app = rx.App()
app.add_page(index, route="/", title="Proposal Generator")
