from robot.api import logger

from ..rpc.protocol import RecordingResult
from ._runonfailure import run_on_failure


class _Recording:

    @run_on_failure
    def start_screen_recording(self, path=None, max_duration=None):
        """Starts recording the device screen.

        ``path`` is the output file path (optional).
        ``max_duration`` is the maximum recording duration in seconds (optional).

        Example:
        | Start Screen Recording |
        | Start Screen Recording | path=/tmp/test.mp4 | max_duration=60 |
        """
        options = {}
        if path:
            options['path'] = path
        if max_duration is not None:
            options['maxDuration'] = int(max_duration)
        self._cache.current.call('startRecording', **options)
        logger.info("Screen recording started")

    @run_on_failure
    def stop_screen_recording(self, filename=None):
        """Stops the screen recording and saves it.

        ``filename`` is the output file path (optional, uses server default).

        Returns a dictionary with recording result: status, duration, file.

        Example:
        | ${result}= | Stop Screen Recording |
        | ${result}= | Stop Screen Recording | filename=test_recording.mp4 |
        """
        result = self._cache.current.call('stopRecording')
        recording = RecordingResult.from_dict(result) if result else RecordingResult(status='stopped')
        logger.info(
            f"Screen recording stopped. Duration: {recording.duration}s, "
            f"File: {recording.file or 'N/A'}"
        )
        return vars(recording)
