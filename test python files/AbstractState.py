class AbstractState:
    # 抽象状态
    def __init__(self, stateStrList, link, state=''):
        self.stateStrList = stateStrList
        self.stateStrDict = dict()
        for i in range(len(self.stateStrList)):
            self.stateStrDict[self.stateStrList[i]] = i
        self.link = link

        if state in self.stateStrList:
            self.stateValue = self.stateStrDict[state]
        else:
            self.stateValue = 0
        self.stateStr = self.stateStrList[self.stateValue]
        return

    def getState(self):
        return self.stateStr

    def toState(self, state):
        if state not in self.stateStrList:
            print('Error : %s is not a valid state to change to! You should pick state from : %s'
                  % (state, self.stateStrList))
            return
        # 查看状态转移矩阵是否允许转移
        if self.link[self.stateValue][self.stateStrDict[state]] == 1:
            self.stateStr = state
            self.stateValue = self.stateStrDict[self.stateStr]
        else:
            print('Warning : Can not change state from %s to %s !'
                  % (self.stateStr, state))


def test():
    # 创建四种状态名称
    stateStrList = ['state1', 'state2', 'state3', 'state4']
    # 创建状态转移矩阵
    link = [[1, 1, 1, 1],
            [1, 1, 0, 1],
            [1, 1, 1, 1],
            [1, 1, 1, 1]]
    # 创建状态对象
    state = AbstractState(stateStrList, link, 'state1')
    # 显示状态
    print(state.getState())
    # 改变状态
    state.toState('state2')
    # 显示状态
    print(state.getState())

    # 不可改变 测试
    state.toState('state3')
    print(state.getState())

    # 非法状态 测试
    state.toState('abc123')
    print(state.getState())


if __name__ == "__main__":
    test()
