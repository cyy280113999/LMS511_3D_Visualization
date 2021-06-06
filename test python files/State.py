import numpy
from AbstractState import AbstractState


class State(AbstractState):

    def __init__(self):
        stateStrList = ['unconnect', 'running', 'setting', 'reading', 'round reading']
        link = [[1 for i in range(len(stateStrList))] for i in range(len(stateStrList))]
        # it's :
            #    [[1,1,1,1],
            #     [1,1,1,1],
            #     [1,1,1,1],
            #     [1,1,1,1]]
        super().__init__(stateStrList, link, 'unconnect')

    def isUnconnect(self):
        return self.stateValue == self.stateStrDict['unconnect']

    # deleted state : connected. Same function as running
    def toConnected(self):
        self.toState('connected')

    def isConnected(self):
        return self.stateValue == self.stateStrDict['connected']

    def toRunning(self):
        self.toState('running')

    def isRunning(self):
        return self.stateValue == self.stateStrDict['running']

    def toSetting(self):
        self.toState('setting')

    def isSetting(self):
        return self.stateValue == self.stateStrDict['setting']

    def toReading(self):
        self.toState('reading')

    def isReading(self):
        return self.stateValue == self.stateStrDict['reading']

    def toRoundReading(self):
        self.toState('round reading')

    def isRoundReading(self):
        return self.stateValue == self.stateStrDict['round reading']

def main():
    state = State()
    print(state.getState())


if __name__ == "__main__":
    main()
