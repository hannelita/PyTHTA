import os
class Solution:
  def __init__(self, value):
        self.value = value


def main():
  # inputFile = input("Please provide the input file: ")
  data = open("data.txt", "r")
  # print(data.readlines())
  time = data.readline().split(' ')
  res = filter(str.strip, time)
  print(res)
  data.close()

main()