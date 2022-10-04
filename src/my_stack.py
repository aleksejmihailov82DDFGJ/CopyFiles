from typing import Any


class MyStack:

    def __init__(self):
        self.array = []

    def push(self, item: Any):
        self.array.append(item)

    def pop(self):
        popped_item = self.array.pop()
        return popped_item

    def peek(self):
        return self.array[-1]

    def count(self):
        return len(self.array)

    def empty(self):
        return len(self.array) == 0

    def __iter__(self):
        self.index = self.count() - 1
        return self

    def __next__(self):
        if self.index < 0:
            raise StopIteration()
        result = self.array[self.index]
        self.index -= 1
        return result

# stack = MyStack()
# stack.push(1)
# stack.push(2)
# stack.push(3)
# stack.push(4)
# print(stack.pop())
# print(stack.peek())
# stack.push(5)
# print(stack.count())
# for v in stack:
#     print(v, end=' ')
