from dataclasses import dataclass


@dataclass
class AgsMap:
    group_row: int = None
    group_row_num: int = None
    heading_row: int = None
    heading_row_num: int = None
    type_row: int = None
    type_row_num: int = None
    unit_row: int = None
    unit_row_num: int = None
    data_row_start: int = None
    data_row_start_num: int = None
    data_row_end: int = None
    data_row_end_num: int = None

    @property
    def data_size(self):
        if self.data_row_start is None or self.data_row_end is None:
            return None
        return self.data_row_end - self.data_row_start