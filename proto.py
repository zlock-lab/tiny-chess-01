# Prototype chess engine (dev-only, not the entry). Board + move gen + alpha-beta.
# Colour: white=0, black=1; piece stored as (colour<<3)|type.
import sys

PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING = 1, 2, 3, 4, 5, 6
WT = {"p": PAWN, "n": KNIGHT, "b": BISHOP, "r": ROOK, "q": QUEEN, "k": KING}
VAL = {PAWN: 100, KNIGHT: 320, BISHOP: 330, ROOK: 500, QUEEN: 900, KING: 10000}
FILES = "abcdefgh"
START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

PST_PAWN = [
    0,0,0,0,0,0,0,0, 50,50,50,50,50,50,50,50,
    10,10,20,30,30,20,10,10, 5,5,10,25,25,10,5,5,
    0,0,0,20,20,0,0,0, 5,-5,-10,0,0,-10,-5,5,
    5,10,10,-20,-20,10,10,5, 0,0,0,0,0,0,0,0]
PST_KNIGHT = [
    -50,-40,-30,-30,-30,-30,-40,-50, -40,-20,0,0,0,0,-20,-40,
    -30,0,10,15,15,10,0,-30, -30,5,15,20,20,15,5,-30,
    -30,0,15,20,20,15,0,-30, -30,5,10,15,15,10,5,-30,
    -40,-20,0,5,5,0,-20,-40, -50,-40,-30,-30,-30,-30,-40,-50]
PST_BISHOP = [
    -20,-10,-10,-10,-10,-10,-10,-20, -10,0,0,0,0,0,0,-10,
    -10,0,5,10,10,5,0,-10, -10,5,5,10,10,5,5,-10,
    -10,0,10,10,10,10,0,-10, -10,10,10,10,10,10,10,-10,
    -10,5,0,0,0,0,5,-10, -20,-10,-10,-10,-10,-10,-10,-20]
PST_ROOK = [
    0,0,0,0,0,0,0,0, 5,10,10,10,10,10,10,5,
    -5,0,0,0,0,0,0,-5, -5,0,0,0,0,0,0,-5,
    -5,0,0,0,0,0,0,-5, -5,0,0,0,0,0,0,-5,
    -5,0,0,0,0,0,0,-5, 0,0,0,5,5,0,0,0]
PST_QUEEN = [
    -20,-10,-10,-5,-5,-10,-10,-20, -10,0,0,0,0,0,0,-10,
    -10,0,5,5,5,5,0,-10, -5,0,5,5,5,5,0,-5,
    0,0,5,5,5,5,0,-5, -10,5,5,5,5,5,0,-10,
    -10,0,5,0,0,0,0,-10, -20,-10,-10,-5,-5,-10,-10,-20]
PST_KING = [
    -30,-40,-40,-50,-50,-40,-40,-30, -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30, -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20, -10,-20,-20,-20,-20,-20,-20,-10,
    20,20,0,0,0,0,20,20, 20,30,10,0,0,10,30,20]
PST = {PAWN: PST_PAWN, KNIGHT: PST_KNIGHT, BISHOP: PST_BISHOP, ROOK: PST_ROOK, QUEEN: PST_QUEEN, KING: PST_KING}


def sq(f, r):
    return r * 8 + f


class Board:
    def __init__(self):
        self.pieces = [0] * 64
        self.side = 0
        self.castle = 0
        self.ep = -1
        self.half = 0
        self.move_no = 1

    def clone(self):
        b = Board()
        b.pieces = self.pieces[:]
        b.side, b.castle, b.ep, b.half, b.move_no = self.side, self.castle, self.ep, self.half, self.move_no
        return b

    @staticmethod
    def from_fen(fen):
        b = Board()
        parts = fen.split()
        rows = parts[0].split("/")
        for r, row in enumerate(rows):
            rank = 7 - r
            f = 0
            for ch in row:
                if ch.isdigit():
                    f += int(ch)
                else:
                    col = 0 if ch.isupper() else 1
                    t = WT[ch.lower()]
                    b.pieces[sq(f, rank)] = (col << 3) | t
                    f += 1
        b.side = 0 if parts[1] == "w" else 1
        if len(parts) > 2:
            b.castle = 0
            if "K" in parts[2]: b.castle |= 1
            if "Q" in parts[2]: b.castle |= 2
            if "k" in parts[2]: b.castle |= 4
            if "q" in parts[2]: b.castle |= 8
            b.ep = -1 if parts[3] == "-" else (FILES.index(parts[3][0]) + (int(parts[3][1]) - 1) * 8)
        if len(parts) > 4: b.half = int(parts[4])
        if len(parts) > 5: b.move_no = int(parts[5])
        return b

    def _king(self, col):
        for i, p in enumerate(self.pieces):
            if p == (col << 3) | KING:
                return i
        return -1

    def _attacked(self, sq_, by):
        f, r = sq_ % 8, sq_ // 8
        if by == 0:  # white pawns attack up (toward rank+1)
            for df in (-1, 1):
                f2, r2 = f + df, r - 1
                if 0 <= f2 < 8 and 0 <= r2 < 8 and self.pieces[sq(f2, r2)] == PAWN:
                    return True
        else:
            for df in (-1, 1):
                f2, r2 = f + df, r + 1
                if 0 <= f2 < 8 and 0 <= r2 < 8 and self.pieces[sq(f2, r2)] == (1 << 3) | PAWN:
                    return True
        for df, dr in ((1,2),(2,1),(2,-1),(1,-2),(-1,-2),(-2,-1),(-2,1),(-1,2)):
            f2, r2 = f + df, r + dr
            if 0 <= f2 < 8 and 0 <= r2 < 8 and self.pieces[sq(f2, r2)] == (by << 3) | KNIGHT:
                return True
        for df in (-1,0,1):
            for dr in (-1,0,1):
                if df == 0 and dr == 0: continue
                f2, r2 = f + df, r + dr
                if 0 <= f2 < 8 and 0 <= r2 < 8 and self.pieces[sq(f2, r2)] == (by << 3) | KING:
                    return True
        for df, dr in ((1,1),(1,-1),(-1,1),(-1,-1)):
            f2, r2 = f + df, r + dr
            while 0 <= f2 < 8 and 0 <= r2 < 8:
                p = self.pieces[sq(f2, r2)]
                if p:
                    if p >> 3 == by and (p & 7) in (BISHOP, QUEEN): return True
                    break
                f2 += df; r2 += dr
        for df, dr in ((1,0),(-1,0),(0,1),(0,-1)):
            f2, r2 = f + df, r + dr
            while 0 <= f2 < 8 and 0 <= r2 < 8:
                p = self.pieces[sq(f2, r2)]
                if p:
                    if p >> 3 == by and (p & 7) in (ROOK, QUEEN): return True
                    break
                f2 += df; r2 += dr
        return False

    def in_check(self, col):
        return self._attacked(self._king(col), col ^ 1)

    def _own(self, p, col):
        return p and p >> 3 == col

    def _foe(self, p, col):
        return p and p >> 3 != col

    def gen_moves(self):
        moves = []
        col = self.side
        for i, p in enumerate(self.pieces):
            if not p or p >> 3 != col: continue
            t = p & 7
            f, r = i % 8, i // 8
            if t == PAWN:
                self._pawn(i, f, r, col, moves)
            elif t == KNIGHT:
                for df, dr in ((1,2),(2,1),(2,-1),(1,-2),(-1,-2),(-2,-1),(-2,1),(-1,2)):
                    f2, r2 = f + df, r + dr
                    if 0 <= f2 < 8 and 0 <= r2 < 8:
                        j = sq(f2, r2); q = self.pieces[j]
                        if not self._own(q, col): moves.append((i, j, 0))
            elif t in (BISHOP, ROOK, QUEEN):
                dirs = []
                if t in (BISHOP, QUEEN): dirs += [(1,1),(1,-1),(-1,1),(-1,-1)]
                if t in (ROOK, QUEEN): dirs += [(1,0),(-1,0),(0,1),(0,-1)]
                for df, dr in dirs:
                    f2, r2 = f + df, r + dr
                    while 0 <= f2 < 8 and 0 <= r2 < 8:
                        j = sq(f2, r2); q = self.pieces[j]
                        if not q:
                            moves.append((i, j, 0))
                        else:
                            if self._foe(q, col): moves.append((i, j, 0))
                            break
                        f2 += df; r2 += dr
            elif t == KING:
                for df in (-1,0,1):
                    for dr in (-1,0,1):
                        if df == 0 and dr == 0: continue
                        f2, r2 = f + df, r + dr
                        if 0 <= f2 < 8 and 0 <= r2 < 8:
                            j = sq(f2, r2); q = self.pieces[j]
                            if not self._own(q, col): moves.append((i, j, 0))
                self._castle(i, col, moves)
        return moves

    def _pawn(self, i, f, r, col, moves):
        dir_ = 1 if col == 0 else -1
        start = 1 if col == 0 else 6
        promo = 7 if col == 0 else 0
        r2 = r + dir_
        if 0 <= r2 < 8 and not self.pieces[sq(f, r2)]:
            self._pawn_push(i, sq(f, r2), promo, moves)
            if r == start and not self.pieces[sq(f, r + 2 * dir_)]:
                moves.append((i, sq(f, r + 2 * dir_), 0))
        for df in (-1, 1):
            f2, r2 = f + df, r + dir_
            if 0 <= f2 < 8 and 0 <= r2 < 8:
                j = sq(f2, r2); q = self.pieces[j]
                if self._foe(q, col):
                    self._pawn_push(i, j, promo, moves)
                elif j == self.ep:
                    moves.append((i, j, 0))

    def _pawn_push(self, i, j, promo, moves):
        if j // 8 == promo:
            for pr in ("q", "r", "b", "n"):
                moves.append((i, j, pr))
        else:
            moves.append((i, j, 0))

    def _castle(self, i, col, moves):
        row = 0 if col == 0 else 7
        if i != sq(4, row): return
        foe = col ^ 1
        king_side = 1 if col == 0 else 4
        queen_side = 2 if col == 0 else 8
        rook_king = sq(7, row); rook_queen = sq(0, row)
        if self.castle & king_side and not self.pieces[sq(5,row)] and not self.pieces[sq(6,row)] \
           and self.pieces[rook_king] == (col << 3) | ROOK \
           and not self._attacked(i, foe) and not self._attacked(sq(5,row), foe) and not self._attacked(sq(6,row), foe):
            moves.append((i, sq(6, row), 0))
        if self.castle & queen_side and not self.pieces[sq(3,row)] and not self.pieces[sq(2,row)] and not self.pieces[sq(1,row)] \
           and self.pieces[rook_queen] == (col << 3) | ROOK \
           and not self._attacked(i, foe) and not self._attacked(sq(3,row), foe) and not self._attacked(sq(2,row), foe):
            moves.append((i, sq(2, row), 0))

    def apply(self, m):
        i, j, promo = m
        col = self.side
        p = self.pieces[i]
        t = p & 7
        if t == PAWN and j == self.ep and not self.pieces[j]:
            self.pieces[sq(j % 8, i // 8)] = 0
        if t == KING and abs(j % 8 - i % 8) == 2:
            if j % 8 == 6:
                self.pieces[sq(7, j // 8)] = 0
                self.pieces[sq(5, j // 8)] = (col << 3) | ROOK
            else:
                self.pieces[sq(0, j // 8)] = 0
                self.pieces[sq(3, j // 8)] = (col << 3) | ROOK
        if t == KING:
            if col == 0: self.castle &= ~3
            else: self.castle &= ~12
        for rm, bit in ((sq(0,0),2),(sq(7,0),1),(sq(0,7),8),(sq(7,7),4)):
            if i == rm or j == rm: self.castle &= ~bit
        self.ep = -1
        if t == PAWN and abs(j // 8 - i // 8) == 2:
            self.ep = sq(i % 8, (i // 8 + j // 8) // 2)
        if t == PAWN or self.pieces[j]: self.half = 0
        else: self.half += 1
        self.pieces[i] = 0
        if promo:
            pt = {"q": QUEEN, "r": ROOK, "b": BISHOP, "n": KNIGHT}[promo]
            self.pieces[j] = (col << 3) | pt
        else:
            self.pieces[j] = p
        self.side = col ^ 1
        if col == 1: self.move_no += 1

    def legal_moves(self):
        out = []
        for m in self.gen_moves():
            b = self.clone(); b.apply(m)
            if not b.in_check(self.side):
                out.append(m)
        return out

    def evaluate(self):
        s = 0
        for i, p in enumerate(self.pieces):
            if not p: continue
            col = p >> 3; t = p & 7
            v = VAL[t] + PST[t][i if col == 0 else 63 - i]
            s += v if col == 0 else -v
        return s

    def uci(self, m):
        i, j, promo = m
        u = FILES[i % 8] + str(i // 8 + 1) + FILES[j % 8] + str(j // 8 + 1)
        if promo: u += promo
        return u

    def parse_uci(self, u):
        i = FILES.index(u[0]) + (int(u[1]) - 1) * 8
        j = FILES.index(u[2]) + (int(u[3]) - 1) * 8
        return (i, j, u[4] if len(u) == 5 else 0)


def search(b, depth, alpha, beta, nodes):
    nodes[0] += 1
    if depth == 0:
        return b.evaluate()
    moves = b.legal_moves()
    if not moves:
        return -100000 + b.move_no if b.in_check(b.side) else 0
    col = b.side
    if col == 0:
        best = -10**9
        for m in moves:
            nb = b.clone(); nb.apply(m)
            v = search(nb, depth - 1, alpha, beta, nodes)
            if v > best: best = v
            if best > alpha: alpha = best
            if alpha >= beta: break
        return best
    else:
        best = 10**9
        for m in moves:
            nb = b.clone(); nb.apply(m)
            v = search(nb, depth - 1, alpha, beta, nodes)
            if v < best: best = v
            if best < beta: beta = best
            if alpha >= beta: break
        return best


def best_move(b, depth):
    moves = b.legal_moves()
    if not moves: return None, 0, 0
    nodes = [0]; col = b.side
    best = None; bestv = -10**9 if col == 0 else 10**9
    alpha, beta = -10**9, 10**9
    for m in moves:
        nb = b.clone(); nb.apply(m)
        v = search(nb, depth - 1, alpha, beta, nodes)
        if col == 0:
            if v > bestv: bestv, best = v, m
            if bestv > alpha: alpha = bestv
        else:
            if v < bestv: bestv, best = v, m
            if bestv < beta: beta = bestv
    return best, bestv, nodes[0]


if __name__ == "__main__":
    b = Board.from_fen(START_FEN)
    print("legal start moves:", len(b.legal_moves()))
    print("static eval:", b.evaluate())
    import time
    t = time.time()
    mv, v, n = best_move(b, 3)
    print("best:", b.uci(mv), "eval", v, "nodes", n, "time", round(time.time()-t, 2))
