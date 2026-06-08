from oic_doc_generator.api.job_manager import (
    advance_step,
    update_activity
)

class ProgressTracker:

    def __init__(self, total_points):
        self.total_points = total_points
        self.current_points = 0

    def advance(
        self,
        job_id,
        component,
        detail,
        current_item=None,
        total_items=None,
        points=1
    ):

        self.current_points += points

        percent = int(
            (self.current_points / self.total_points)
            * 100
        )

        if percent > 100:
            percent = 100

        if current_item and total_items:

            message = (
                f"{component} | "
                f"{detail} | "
                f"{current_item}/{total_items}"
            )

        else:

            message = (
                f"{component} | {detail}"
            )

        update_activity(
            job_id,
            message
        )

        advance_step(
            job_id,
            percent
        )