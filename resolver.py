import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from resistor import Resistor
from capacitor import Capacitor
from inductor import Inductor
import ipdb

class Resolver:
  def __init__(self):
    self.df = None
    self.sources = []
    self.nodes = []
    self.elements = None
    self.g_matrix = None

  def build(self):
    self.import_file()
    self.get_info()
    self.build_elements()
    self.build_g_matrix()
    self.simulation()
  
  def import_file(self):
    self.df = pd.read_csv('test.csv', header=None)
    return self.df

  def get_info(self):
    build_info = np.array(self.df[:1]).reshape(10,)
    self.nodes_qty = build_info[1]
    self.sources_qty = build_info[2]
    self.dt = build_info[3]
    self.tmax = build_info[4]
    self.elements = self.df.drop([0])
    self.elements = self.elements[:-1]

  def build_elements(self):
    self.ndcvs = 0
    self.ndccs = 0
    self.energy_storage_el = 0
    self.gkm = np.zeros(self.elements.shape[0])
    self.nh = 0
    for index, row in self.elements.iterrows():
      if row[0] == 'R':
        resistor = Resistor(row[3])
        self.gkm[index-1] = 1/resistor.value
        self.nh = self.nh + 1
      elif row[0] == 'C':
        capacitor = Capacitor((row[3]*1e-6))
        self.gkm[index-1] = 2*capacitor.value/self.dt
        self.nh = self.nh + 1
      elif row[0] == 'L':
        inductor = Inductor((row[3]*1e-3))
        self.gkm[index-1] = self.dt/(2*inductor.value)
      elif row[0] == 'EDC':
        self.ndcvs = self.ndcvs + 1

  def build_g_matrix(self):
    self.g_matrix = np.zeros((self.elements.shape[0], self.elements.shape[0]))
    # print(self.g_matrix[0,0])
    for index, row in self.elements.iterrows():
      k = row[1]
      m = row[2]
      if m == 0:
        self.g_matrix[k,k] = self.g_matrix[k,k] + self.gkm[index-1]
      elif k == 0:
        self.g_matrix[m,m] = self.g_matrix[m,m] + self.gkm[index-1]
      else:
        self.g_matrix[k,k] = self.g_matrix[k,k] + self.gkm[index-1]
        self.g_matrix[m,m] = self.g_matrix[m,m] + self.gkm[index-1]
        self.g_matrix[k,m] = self.g_matrix[k,m] + self.gkm[index-1]
        self.g_matrix[m,k] = self.g_matrix[m,k] + self.gkm[index-1]
    # print(self.g_matrix)
    d = self.nodes_qty - self.sources_qty
    self.gaa = self.g_matrix[0:d, 0:d]
    self.gab = self.g_matrix[0:d, d:self.nodes_qty]
    self.gba = self.g_matrix[d:self.nodes_qty, 0:d]
    self.gbb = self.g_matrix[d:self.nodes_qty, d:self.nodes_qty]
    # print(self.gbb)

  def simulation(self):
    n = 0
    self.npoints = np.fix(self.tmax/self.dt) + 1
    while (n <= self.npoints):
      time = 0
      THTACtl = 1
      x = 0
      
      self.i_matrix = np.zeros(self.nodes_qty)
      self.ia_matrix = np.zeros(self.nodes_qty - self.sources_qty)
      self.v_matrix = np.zeros((self.nodes_qty, int(self.npoints)))
      self.va_matrix = np.zeros(self.nodes_qty - self.sources_qty)
      self.vb_matrix = np.zeros(self.sources_qty)
      self.ih_matrix = np.zeros(self.nh)
      self.ihnew_matrix = self.ih_matrix
      self.ihold_matrix = self.ih_matrix
      idxhist_vec = self.elements[7]

      for index, row in self.elements.iterrows():
        k = row[1]
        m = row[2]
        idxhist = idxhist_vec[index]
        # ipdb.set_trace()
        if row[0] == 'L':
          if k == 0:
            self.ihnew_matrix[idxhist] = 2 * self.gkm[index-1] * self.v_matrix[m,n] + self.ihold_matrix[idxhist]
          elif m == 0:
            self.ihnew_matrix[idxhist] = -2 * self.gkm[index-1] * self.v_matrix[k,n] + self.ihold_matrix[idxhist]
          else:
            self.ihnew_matrix[idxhist] = -2 * self.gkm[b] * (self.v_matrix[k,n]-self.v_matrix[m,n]) + self.ihold_matrix[idxhist]
        elif row[0] == 'C':
          if k == 0:
            self.ihnew_matrix[idxhist] = -2 * self.gkm[index-1] * self.v_matrix[m,n] - self.ihold_matrix[idxhist]
          elif m == 0:
            self.ihnew_matrix[idxhist] = 2 * self.gkm[index-1] * self.v_matrix[k,n] - self.ihold_matrix[idxhist]
          else:
            self.ihnew_matrix[idxhist] = 2 * self.gkm[index-1] * (self.v_matrix[k,n]-self.v_matrix[m,n]) - self.ihold_matrix[idxhist]
        elif row[0] == 'EDC':
          self.vb_matrix[x]= row[3];
          x = x+1
      self.ih_matrix = self.ihnew_matrix
      time = time + self.dt
      n = n + 1
      self.i_matrix = np.zeros(self.nodes_qty)
      for index, row in self.elements.iterrows():
        k = row[1]
        m = row[2]
        idxhist = idxhist_vec[index]
        if (row[0] == 'L' or row[0] == 'C'):
          if k == 0:
            self.i_matrix[m]= self.i_matrix[m] - self.ih_matrix[idxhist]
          elif m == 0:
            self.i_matrix[k]= self.i_matrix[k] + self.ih_matrix[idxhist]
          else:
            self.i_matrix[k]= self.i_matrix[k] + self.ih_matrix[idxhist]
            self.i_matrix[m]= self.i_matrix[m] - self.ih_matrix[idxhist]

      d = self.nodes_qty - self.sources_qty
      
      self.rhsa = np.subtract(self.ia_matrix, np.multiply(self.gab, self.vb_matrix))
      # print(self.rhsa)
      with np.errstate(divide='ignore', invalid='ignore'):
        self.va_matrix = np.divide(self.gaa, self.rhsa)
        self.ib_matrix = np.add(np.multiply(self.gba, self.va_matrix), np.multiply(self.gbb, self.vb_matrix))
      # self.i_matrix = np.concatenate((self.ia_matrix, self.ib_matrix))
      
      
      # V(:, n) = [VA; VB];
      print(self.ib_matrix)





