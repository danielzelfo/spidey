# A ranking class to add more points to web pages that have query tokens in titles or headings
class Ranking:
    @staticmethod
    def positionsToRank(positions, extentList = None):
        # Function to check if position is in headings or titles
        def included(extentlist, pos):
            for e in extentlist:
                if pos >= e[0] and pos <= e[1]:
                    return True
            return False
        
        # Addtional points if token appears in headings or titles
        titleconst = 25
        
        importantTagConsts = {
            "h1": 5,
            "h2": 3,
            "h3": 2,
            "b": 1.2,
            "strong": 1.2
        }
        rank = 0
        
        # Loop through positions and check if any of those position is in headgins or titles, if yes then add more points accordingly
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