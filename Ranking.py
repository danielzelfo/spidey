
class Ranking:
    @staticmethod
    def positionsToRank(positions):
        rank = 0
        for pos in positions:
            if pos < 0: # title has 2 times more importance
                rank += 2
            else:
                rank += 1
        return rank