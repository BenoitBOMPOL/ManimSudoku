"""
    Main function
"""
from manim import *
from structs.sudoku import Sudoku

GRID : list[list[int]] = [\
    [int(s) for s in "001000700"],
    [int(s) for s in "000010485"],
    [int(s) for s in "840600030"],
    [int(s) for s in "500190000"],
    [int(s) for s in "003500006"],
    [int(s) for s in "000000500"],
    [int(s) for s in "059300640"],
    [int(s) for s in "180720003"],
    [int(s) for s in "300000000"]
    
]

SUDOKU = Sudoku(GRID)

def get_pos_in_grid_from_rowid_colid(row_id: int, col_id: int):
    return 3*LEFT + 0.75 * RIGHT * col_id + 3*UP + 0.75 * DOWN * row_id

def get_pos_in_dgrid_from_rowid_colid(row_id: int, col_id: int):
    nb_sauts_col = col_id // 3
    h_pos = 6.75*LEFT + (col_id + nb_sauts_col) * 0.25 * RIGHT
    nb_sauts_row = row_id // 3
    v_pos = 1.25 * UP + (row_id + nb_sauts_row) * 0.25 * DOWN
    return h_pos + v_pos

class BuildBackground(Scene):
    def construct(self):
        hlines : list[Line] = []
        vlines : list[Line] = []
        delta = -3.375
        for _ in range(4):
            hlines.append(Line(start = 3.375 * LEFT + delta * DOWN, end = 3.375 * RIGHT + delta * DOWN))
            vlines.append(Line(start = 3.375 * UP + delta * RIGHT, end = 3.375 * DOWN + delta * RIGHT))
            delta += 2.25
        self.play(*[Create(line) for line in hlines + vlines])
        self.wait()

class BuildDGridBackground(Scene):
    def construct(self):
        lines = []
        for i in range(4):
            lines.append(Line(start = (4 + i) * LEFT + 1.5 * UP, end = (4 + i) * LEFT + 1.5 * DOWN))
            lines.append(Line(start = 7 * LEFT + (1.5 - i) * UP, end = 4 * LEFT + (i - 1.5)* DOWN))
            
        self.play(*[Create(line) for line in lines])

class InitGrid(Scene):
    def construct(self):
        vals_txts : list[Text] = []
        for row_id in range(9):
            for col_id in [c_id for c_id in range(9) if SUDOKU.grid[row_id][c_id] > 0]:
                pos_in_grid = get_pos_in_grid_from_rowid_colid(row_id, col_id)
                val_txt = Text(str(SUDOKU.grid[row_id][col_id])).scale(0.5).move_to(pos_in_grid)
                vals_txts.append(val_txt)
        self.play(*[Write(val_txt) for val_txt in vals_txts])
        self.wait()

class CheckIfIsEmpty(Scene):
    def construct(self):
        square = Square(side_length = 0.5, color = WHITE).move_to(get_pos_in_grid_from_rowid_colid(0, 0))
        self.play(Create(square))
        for row_id in range(9):
            for col_id in range(9):
                pos_in_grid = get_pos_in_grid_from_rowid_colid(row_id, col_id)
                if SUDOKU.grid[row_id][col_id] == 0:
                    square.set_color(GREEN)
                else:
                    square.set_color(RED)
                square.move_to(pos_in_grid)
                self.wait(0.25)

class UpdatesFromAllowed(Scene):
    def construct(self):
        global SUDOKU
        square = Square(side_length = 0.5, color = WHITE)
        square_has_been_added = False
        updates_from_allowed : list[tuple[int, int, int]] = []
        txt_updates : list[Text] = []
        
        for row_id in range(9):
            for col_id in [c_id for c_id in range(9) if SUDOKU.grid[row_id][c_id] == 0]:
                pos_in_grid = get_pos_in_grid_from_rowid_colid(row_id, col_id)
                square.move_to(pos_in_grid)
                if not square_has_been_added:
                    self.play(Create(square))
                    square_has_been_added = True
                # IN_GRID, EST-CE QUE TU BZ
                square.move_to(pos_in_grid)
                
                if SUDOKU.grid[row_id][col_id] == 0:
                    annotated_vals = SUDOKU.get_allowed_values(row_id, col_id)
                    if len(annotated_vals) == 1:
                        square.set_color(TEAL)
                        val = annotated_vals[0]
                        SUDOKU.grid[row_id][col_id] = val
                        new_upd_txt = Text(str(val)).scale(0.5).set_color(TEAL).move_to(pos_in_grid)
                        txt_updates.append(new_upd_txt)
                        self.play(Write(new_upd_txt))
                        updates_from_allowed.append((row_id, col_id, val))
                        square.set_color(WHITE)
                    self.wait(0.25)

        for txt_update in txt_updates:
            txt_update.set_color(WHITE)
        
        if square_has_been_added:
            self.play(Uncreate(square))
        return updates_from_allowed

class UpdateFromExtrapolation(Scene):
    def construct(self, val):
        updates : list[tuple[int, int, int]] = []

        dgrid : list[list[bool]] = [[SUDOKU.grid[row_id][col_id] == val for col_id in range(9)] for row_id in range(9)]
        is_complete = True
        for row in dgrid:
            if True not in row:
                is_complete = False
        if is_complete:
            return []

        egrid : list[list[bool]] = SUDOKU.build_extrapolation_grid(val)
        square_already_added_before : list[list[bool]] = [[False for __ in range(9)] for _ in range(9)]

        noice_txt = Text(f"Zone couverte par les {val}").scale(0.35)
        pos_noice_text = get_pos_in_dgrid_from_rowid_colid(-1, 4)
        noice_txt.move_to(pos_noice_text)
        self.add(noice_txt)

        smol_detected_squares = []
        for row_id in range(9):
            for col_id in [c_id for c_id in range(9) if SUDOKU.grid[row_id][c_id] == val]:
                if not square_already_added_before[row_id][col_id]:
                    square_already_added_before[row_id][col_id] = True
                    smol_square = Square(side_length=0.2).move_to(get_pos_in_dgrid_from_rowid_colid(row_id, col_id))
                    smol_square.set_fill(WHITE, 1.0)
                    smol_detected_squares.append(smol_square)
        self.add(*[smol_square for smol_square in smol_detected_squares])
        self.wait()

        smol_row_squares = []
        for row_id in range(9):
            if True in dgrid[row_id]:
                for col_id in range(9):
                    if not square_already_added_before[row_id][col_id]:
                        square_already_added_before[row_id][col_id] = True
                        pos = get_pos_in_dgrid_from_rowid_colid(row_id, col_id)
                        smol_row_square = Square(side_length = 0.2).move_to(pos).set_fill(WHITE, 1.0)
                        smol_row_squares.append(smol_row_square)
        self.add(*[smol_row_square for smol_row_square in smol_row_squares])
        self.wait(DEFAULT_WAIT_TIME / 4)

        smol_col_squares = []
        for col_id in range(9):
            if True in [dgrid[r_id][col_id] for r_id in range(9)]:
                for row_id in range(9):
                    if not square_already_added_before[row_id][col_id]:
                        square_already_added_before[row_id][col_id] = True
                        pos = get_pos_in_dgrid_from_rowid_colid(row_id, col_id)
                        smol_col_square = Square(side_length = 0.2).move_to(pos).set_fill(WHITE, 1.0)
                        smol_col_squares.append(smol_col_square)
        self.add(*[smol_col_square for smol_col_square in smol_col_squares])
        self.wait(DEFAULT_WAIT_TIME / 4)
        
        smol_bloc_squares = []
        for bloc_id in range(9):
            if True in [dgrid[r_id][c_id] for (r_id, c_id) in Sudoku.get_rows_cols_from_bloc_id(bloc_id)]:
                for (row_id, col_id) in Sudoku.get_rows_cols_from_bloc_id(bloc_id):
                    if not square_already_added_before[row_id][col_id]:
                        square_already_added_before[row_id][col_id] = True
                        pos = get_pos_in_dgrid_from_rowid_colid(row_id, col_id)
                        smol_bloc_square = Square(side_length = 0.2).move_to(pos).set_fill(WHITE, 1.0)
                        smol_bloc_squares.append(smol_bloc_square)
        self.add(*[smol_bloc_square for smol_bloc_square in smol_bloc_squares])
        self.wait(DEFAULT_WAIT_TIME / 4)

        smol_remaining_squares = []
        for (row_id, col_id) in sum([[(r_id, c_id) for c_id in range(9)] for r_id in range(9)], []):
            if egrid[row_id][col_id] and not square_already_added_before[row_id][col_id]:
                square_already_added_before[row_id][col_id] = True
                pos = get_pos_in_dgrid_from_rowid_colid(row_id, col_id)
                smol_remaining_square = Square(side_length = 0.2).move_to(pos).set_fill(WHITE, 1.0)
                smol_remaining_squares.append(smol_remaining_square)
        
        self.add(*[smol_rem_square for smol_rem_square in smol_remaining_squares])
        self.wait()

        already_accounted_for : list[tuple[int, int]] = []
        green_squares = []
        new_txts_in_grid = []

        # Row Check
        for row_id in range(9):
            row = egrid[row_id]
            if len(row) == sum(row) + 1:
                col_id = [c_id for c_id in range(9) if not egrid[row_id][c_id]][0]
                if (row_id, col_id) not in already_accounted_for:
                    already_accounted_for.append((row_id, col_id))
                    updates.append((row_id, col_id, val))
                    pos = get_pos_in_dgrid_from_rowid_colid(row_id, col_id)
                    smol_green_square = Square(side_length=0.2).move_to(pos).set_fill(GREEN, 1.0)
                    green_squares.append(smol_green_square)
                    
                    pos_in_grid = get_pos_in_grid_from_rowid_colid(row_id, col_id)
                    new_txt_in_grid = Text(str(val), color = TEAL).scale(0.5).move_to(pos_in_grid)
                    new_txts_in_grid.append(new_txt_in_grid)
                    self.play(
                        Create(smol_green_square),
                        Write(new_txt_in_grid)
                    )
                    SUDOKU.grid[row_id][col_id] = val

        # Row Check
        for col_id in range(9):
            col = [egrid[r_id][col_id] for r_id in range(9)]
            if len(col) == sum(col) + 1:
                row_id = [r_id for r_id in range(9) if not egrid[r_id][col_id]][0]
                if (row_id, col_id) not in already_accounted_for:
                    already_accounted_for.append((row_id, col_id))
                    updates.append((row_id, col_id, val))
                    pos = get_pos_in_dgrid_from_rowid_colid(row_id, col_id)
                    smol_green_square = Square(side_length=0.2).move_to(pos).set_fill(GREEN, 1.0)
                    green_squares.append(smol_green_square)
                    
                    pos_in_grid = get_pos_in_grid_from_rowid_colid(row_id, col_id)
                    new_txt_in_grid = Text(str(val), color = TEAL).scale(0.5).move_to(pos_in_grid)
                    new_txts_in_grid.append(new_txt_in_grid)
                    self.play(
                        Create(smol_green_square),
                        Write(new_txt_in_grid)
                    )
                    SUDOKU.grid[row_id][col_id] = val

        # Bloc Check
        for bloc_id in range(9):
            bloc = [egrid[r_id][c_id] for (r_id, c_id) in Sudoku.get_rows_cols_from_bloc_id(bloc_id)]
            if len(bloc) == sum(bloc) + 1:
                row_id, col_id = [(r_id, c_id) for (r_id, c_id) in Sudoku.get_rows_cols_from_bloc_id(bloc_id) if not egrid[r_id][c_id]][0]
                if (row_id, col_id) not in already_accounted_for:
                    already_accounted_for.append((row_id, col_id))
                    updates.append((row_id, col_id, val))
                    pos = get_pos_in_dgrid_from_rowid_colid(row_id, col_id)
                    smol_green_square = Square(side_length=0.2).move_to(pos).set_fill(GREEN, 1.0)
                    green_squares.append(smol_green_square)
                    
                    pos_in_grid = get_pos_in_grid_from_rowid_colid(row_id, col_id)
                    new_txt_in_grid = Text(str(val), color = TEAL).scale(0.5).move_to(pos_in_grid)
                    new_txts_in_grid.append(new_txt_in_grid)
                    self.play(
                        Create(smol_green_square),
                        Write(new_txt_in_grid)
                    )
                    SUDOKU.grid[row_id][col_id] = val            

        self.remove(*smol_detected_squares)
        self.remove(*smol_row_squares)
        self.remove(*smol_col_squares)
        self.remove(*smol_bloc_squares)
        self.remove(*smol_remaining_squares)
        self.remove(*green_squares)
        self.remove(noice_txt)
        
        for new_txt_in_grid in new_txts_in_grid:
            new_txt_in_grid.set_color(WHITE)

        self.wait()

        return updates


class UpdateFromExtrapolations(Scene):
    def construct(self):
        updates = []
        for val in range(1, 10):
            val_up = UpdateFromExtrapolation.construct(self, val)
            updates.extend(val_up)
        return updates

class UpdatesFromStuckPosition(Scene):
    def construct(self):
        updates_from_stuck : list[tuple[int, int, int]] = []
        for bloc_id in range(9):
            rowcol_from_bloc = Sudoku.get_rows_cols_from_bloc_id(bloc_id)
            available_rc_in_bloc = [(r, c) for  (r, c) in rowcol_from_bloc if SUDOKU.grid[r][c] == 0]

            pos_where_val_is_allowed : dict[int, list[tuple[int, int]]] = {val : [] for val in range(1, 10)}
            for row_id, col_id in available_rc_in_bloc:
                allowed_vals = SUDOKU.get_allowed_values(row_id, col_id)
                for allowed_val in allowed_vals:
                    pos_where_val_is_allowed[allowed_val].append((row_id, col_id))
            
            # print(f"{bloc_id = }")
            for val in range(1, 10):
                if len(pos_where_val_is_allowed[val]) > 0:
                    all_rows_where_val_could_be_in_bloc = list(set([row_id for (row_id, _) in pos_where_val_is_allowed[val]]))
                    all_cols_where_val_could_be_in_bloc = list(set([col_id for (_, col_id) in pos_where_val_is_allowed[val]]))
                    if len(all_rows_where_val_could_be_in_bloc) == 1:
                        row_id = all_rows_where_val_could_be_in_bloc[0]
                        empty_cells_in_row = [c_id for c_id in range(9) if SUDOKU.grid[row_id][c_id] == 0]
                        remaining_empty_cells_row = [c_id for c_id in empty_cells_in_row if Sudoku.get_bloc_id(row_id, c_id) != bloc_id]
                        allowed_vals : dict = {c_id : SUDOKU.get_allowed_values(row_id, c_id) for c_id in remaining_empty_cells_row}
                        for c_id in allowed_vals.keys():
                            allowed_vals[c_id] = [v for v in allowed_vals[c_id] if v != val]
                        for c_id in allowed_vals.keys():
                            if len(allowed_vals[c_id]) == 1:
                                col_id = c_id
                                only_allowed_val = allowed_vals[col_id][0]
                                pos_in_grid = get_pos_in_grid_from_rowid_colid(row_id, col_id)
                                self.play(Write(Text(str(only_allowed_val)).scale(0.5).move_to(pos_in_grid)))
                                SUDOKU.grid[row_id][col_id] = only_allowed_val
                                updates_from_stuck.append((row_id, col_id, only_allowed_val))

                    elif len(all_cols_where_val_could_be_in_bloc) == 1:
                        col_id = all_cols_where_val_could_be_in_bloc[0]
                        empty_cells_in_col = [r_id for r_id in range(9) if SUDOKU.grid[r_id][col_id] == 0]
                        remaining_empty_cells_col = [r_id for r_id in empty_cells_in_col if Sudoku.get_bloc_id(r_id, col_id) != bloc_id]
                        allowed_vals_col = {r_id : SUDOKU.get_allowed_values(r_id, col_id) for r_id in remaining_empty_cells_col}
                        for r_id in allowed_vals_col.keys():
                            allowed_vals_col[r_id] = [v for v in allowed_vals_col[r_id] if v != val]
                        for r_id in allowed_vals_col.keys():
                            if len(allowed_vals_col[r_id]) == 1:
                                row_id = r_id
                                only_allowed_val = allowed_vals_col[row_id][0]
                                pos_in_grid = get_pos_in_grid_from_rowid_colid(row_id, col_id)
                                self.play(Write(Text(str(only_allowed_val)).scale(0.5).move_to(pos_in_grid)))
                                SUDOKU.grid[row_id][col_id] = only_allowed_val
                                updates_from_stuck.append((row_id, col_id, only_allowed_val))
        return updates_from_stuck

class MainSudoku(Scene):
    def construct(self):
        print(SUDOKU)
        BuildBackground.construct(self)
        InitGrid.construct(self)
        BuildDGridBackground.construct(self)

        has_been_updated = True
        while has_been_updated:
            has_been_updated = False
            has_been_updated = has_been_updated or len(UpdatesFromAllowed.construct(self)) > 0
            has_been_updated = has_been_updated or len(UpdateFromExtrapolations.construct(self)) > 0
            if not has_been_updated:
                updates_from_stuck_position = UpdatesFromStuckPosition.construct(self)
                print("***** START UPDATES FROM STUCK_POSITION *****")
                for (row_id, col_id, val) in updates_from_stuck_position:
                    print(f"S[{row_id}][{col_id}] = {val}")
                print("***** END OF UPDATES FROM STUCK_POSITION *****")     
                has_been_updated = len(updates_from_stuck_position) > 0
        print(SUDOKU)

        for row_id in range(9):
            for col_id in [c_id for c_id in range(9) if SUDOKU.grid[row_id][c_id] == 0]:
                print(f"Allowed vals @[{row_id}][{col_id}] = {SUDOKU.get_allowed_values(row_id, col_id)}")
            print()