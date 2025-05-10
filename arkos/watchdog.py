import datetime
import logging
import threading
import time
from multiprocessing.synchronize import Event as MpEvent

from arkos.object_detection.base import ObjectDetectProcess
from arkos.util.services import restart_arkos

logger = logging.getLogger(__name__)


class ArkosWatchdog(threading.Thread):
    def __init__(self, detectors: dict[str, ObjectDetectProcess], stop_event: MpEvent):
        super().__init__(name="arkos_watchdog")
        self.detectors = detectors
        self.stop_event = stop_event

    def run(self) -> None:
        time.sleep(10)
        while not self.stop_event.wait(10):
            now = datetime.datetime.now().timestamp()

            # check the detection processes
            for detector in self.detectors.values():
                detection_start = detector.detection_start.value  # type: ignore[attr-defined]
                # issue https://github.com/python/typeshed/issues/8799
                # from mypy 0.981 onwards
                if detection_start > 0.0 and now - detection_start > 10:
                    logger.info(
                        "Detection appears to be stuck. Restarting detection process..."
                    )
                    detector.start_or_restart()
                elif (
                    detector.detect_process is not None
                    and not detector.detect_process.is_alive()
                ):
                    logger.info("Detection appears to have stopped. Exiting Arkos...")
                    restart_arkos()

        logger.info("Exiting watchdog...")
