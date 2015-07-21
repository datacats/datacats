import unittest

from datacats.cli.util import CliProgressTracker
import random


class TestCliProgressTracker(unittest.TestCase):
    def test_progress_tracker(self):
        with CliProgressTracker(
            task_title="Title for test progress bar",
            total=13) as pt:
            for i in range(14):
                pt.update_state(
                    state='PROGRESS',
                    meta={
                        'current': i,
                        'total': 13,
                        'status': 'wo' * random.randint(3, 14)}
                    )
            pt.update_state(
                state='BANANA',
                meta={
                    'current': 12,
                    'total': 13,
                    'status': 'wo' * random.randint(3, 14)}
                )
