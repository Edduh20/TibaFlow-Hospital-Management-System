import sys

class CustomException(Exception):
    def __init__(self, error_message, error_detail: sys):
        super().__init__(error_message)
        _, _, exc_tb = error_detail.exc_info()
        self.lineno = exc_tb.tb_lineno
        self.filename = exc_tb.tb_frame.f_code.co_filename
        self.error_message = error_message

    def __str__(self):
        return (
            f"Error in [{self.filename}] "
            f"at line [{self.lineno}]: "
            f"{self.error_message}"
        )
