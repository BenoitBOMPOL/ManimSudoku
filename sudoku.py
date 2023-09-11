"""
    Sudoku class
"""
from copy import deepcopy
from time import sleep

class Sudoku:
    def __init__(self, grid : list[list[int]]):
        self.grid : list[list[int]] = deepcopy(grid)
    
    def __str__(self):
        output : str = "-" * 25 + "\n"
        for line_id, line in enumerate(self.grid):
            output = output + "| "
            for region_id in range(3):
                region = [str(i) if i > 0 else " " for i in line[3*region_id:3*(region_id + 1)]]
                output = output + " ".join(region) + " | "
            output = output + "\n" 
            if line_id % 3 == 2:
                output = output + 25 * "-" + "\n"
        return output

    def get_vals_in_bloc(self, bloc_id: int) -> list[int]:
        all_vals_in_bloc : list[int] = []
        for (row_id, col_id) in Sudoku.get_rows_cols_from_bloc_id(bloc_id):
            if self.grid[row_id][col_id] > 0:
                all_vals_in_bloc.append(self.grid[row_id][col_id])
        return all_vals_in_bloc
    
    def get_vals_in_row(self, row_id: int) -> list[int]:
        vals_in_row : list[int] = [val for val in self.grid[row_id] if val > 0]
        return vals_in_row
    
    def get_empty_cell_count(self) -> int:
        return sum([val == 0 for val in sum(self.grid, [])])

    
    def get_vals_in_col(self, col_id: int) -> list[int]:
        vals_in_col : list[int] = [val for val in [self.grid[row_id][col_id] for row_id in range(9)] if val > 0]
        return vals_in_col
    
    def get_allowed_values(self, row_id: int, col_id: int) -> list[int]:
        assert self.grid[row_id][col_id] == 0
        allowed_values : list[int] = list(range(1, 10))
        in_same_row  : list[int] = self.get_vals_in_row(row_id)
        in_same_col  : list[int] = self.get_vals_in_col(col_id)
        in_same_bloc : list[int] = self.get_vals_in_bloc(self.get_bloc_id(row_id, col_id))
        return [val for val in allowed_values if (val not in in_same_row) and (val not in in_same_col) and (val not in in_same_bloc)]
    
    def get_updates_from_allowed_values(self) -> list[tuple[int, int, int]]:
        """
            (row_id, col_id, val_found)
        """
        updates : list[tuple[int, int, int]] = []
        for row_id in range(9):
            for col_id in [c_id for c_id in range(9) if self.grid[row_id][c_id] == 0]:
                allowed_vals = self.get_allowed_values(row_id, col_id)
                if len(allowed_vals) == 1:
                    updates.append((row_id, col_id, allowed_vals[0]))
        return list(set(updates))

    @staticmethod
    def get_bloc_id(row_id: int, col_id: int) -> int:
        return 3*(row_id // 3) + (col_id // 3)
    
    @staticmethod
    def get_rows_cols_from_bloc_id(bloc_id: int) -> list[tuple[int, int]]:
        all_rows_cols : list[tuple[int, int]] = []
        for row_id in range(9):
            for col_id in range(9):
                if Sudoku.get_bloc_id(row_id, col_id) == bloc_id:
                    all_rows_cols.append((row_id, col_id))
        return all_rows_cols
    
    def build_detection_grid(self, val: int) -> list[list[bool]]:
        detection_grid : list[list[bool]] = [[False for __ in range(9)] for _ in range(9)]
        for row_id in range(9):
            for col_id in [c_id for c_id in range(9) if self.grid[row_id][c_id] == val]:
                detection_grid[row_id][col_id] = True
        return detection_grid

    def build_extrapolation_grid(self, val: int) -> list[list[bool]]:
        detection_grid: list[list[bool]] = self.build_detection_grid(val)
        extrapolation_grid: list[list[bool]] = [[False for __ in range(9)] for _ in range(9)]

        # Line Check
        for row_id, row in enumerate(detection_grid):
            if sum(row) == 1:
                for col_id in range(9):
                    extrapolation_grid[row_id][col_id] = True
        
        # Col Check
        for col_id in range(9):
            col = [detection_grid[row_id][col_id] for row_id in range(9)]
            if sum(col) == 1:
                for row_id in range(9):
                    extrapolation_grid[row_id][col_id] = True
        
        # Bloc Check
        for bloc_id in range(9):
            all_rowscols_in_bloc = Sudoku.get_rows_cols_from_bloc_id(bloc_id)
            detecgrid_vals_in_bloc = [detection_grid[row_id][col_id] for (row_id, col_id) in all_rowscols_in_bloc]
            if sum(detecgrid_vals_in_bloc) == 1:
                for (row_id, col_id) in all_rowscols_in_bloc:
                    extrapolation_grid[row_id][col_id] = True
        
        extrapolation_grid = [[extrapolation_grid[row_id][col_id] or (self.grid[row_id][col_id] > 0) for col_id in range(9)] for row_id in range(9)]

        return extrapolation_grid

    def get_updates_from_extrapolation_grid(self, extrapolation_grid: list[list[bool]], val : int) -> list[tuple[int, int, int]]:
        all_updates : list[tuple[int, int, int]] = []
        # Check for row updates
        for row_id, row in enumerate(extrapolation_grid):
            if len(row) == sum(row) + 1:
                col_id = [j for j, b in enumerate(row) if not b][0]
                all_updates.append((row_id, col_id, val))
        
        # Check for col updates
        for col_id in range(9):
            col = [extrapolation_grid[row_id][col_id] for row_id in range(9)]
            if len(col) == sum(col) + 1:
                row_id = [i for i, b in enumerate(col) if not b][0]
                all_updates.append((row_id, col_id, val))
        
        # Check for bloc updates
        for bloc_id in range(9):
            all_rowscols_in_bloc = Sudoku.get_rows_cols_from_bloc_id(bloc_id)
            extrapolation_in_bloc = [extrapolation_grid[row_id][col_id] for (row_id, col_id) in all_rowscols_in_bloc]
            if len(extrapolation_in_bloc) == sum(extrapolation_in_bloc) + 1:
                index_of_rowscols = [i for i, b in enumerate(extrapolation_in_bloc) if not b][0]
                row_id, col_id = all_rowscols_in_bloc[index_of_rowscols]
                all_updates.append((row_id, col_id, val))
        
        return list(set(all_updates))
    
    def get_updates_from_extrapolation(self) -> list[tuple[int, int, int]]:
        all_updates_from_extrapolation : list[tuple[int, int, int]] = []
        for val in range(1, 10):
            egrid_val = self.build_extrapolation_grid(val)
            updates_val = self.get_updates_from_extrapolation_grid(egrid_val, val)
            all_updates_from_extrapolation.extend(updates_val)
        return list(set(all_updates_from_extrapolation))
    
    def full_update(self) -> bool:
        from_allowed : list[tuple[int, int, int]] = self.get_updates_from_allowed_values()
        from_extrapol : list[tuple[int, int, int]] = self.get_updates_from_extrapolation()
        all_updates = list(set(from_allowed + from_extrapol))
        for (row_id, col_id, val) in all_updates:
            self.grid[row_id][col_id] = val
        return len(all_updates) > 0

    def update_while_possible(self, show_grid : bool = True):
        has_been_updated : bool = True
        while has_been_updated:
            has_been_updated = self.full_update()
            if show_grid:
                print(self)
                sleep(1)