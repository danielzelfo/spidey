
class Ranking:
    @staticmethod
    def positionsToRank(positions):
        titleconst = 5

        rank = 0
        for pos in positions:
            if pos < 0: # title is more importance
                rank += titleconst
            else:
                rank += 1
        return rank