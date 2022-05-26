import time

class Ranking:
    @staticmethod
    def positionsToRank(positions, extentList = None):
        def included(extentlist, pos):
            for e in extentlist:
                if pos >= e[0] and pos <= e[1]:
                    return True
            return False


        titleconst = 10
        
        importantTagConsts = {
            "h1": 5,
            "h2": 3,
            "h3": 2,
            "b": 1.2,
            "strong": 1.2
        }
        rank = 0
        
        for pos in positions:
            if pos < 0: # title is more important
                rank += titleconst
                continue

            cont = False
            for etag in extentList:
                if included(extentList[etag], pos):
                    rank += importantTagConsts[etag]
                    cont = True
                    break
            if cont:
                continue
            

            rank += 1
        return rank