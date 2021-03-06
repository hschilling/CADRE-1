""" Plots our objective and constraint histories from the current data in
data.dmp. You can do this while the model is running."""

from six.moves import range

import numpy as np
from matplotlib import pylab

from openmdao.core.mpi_wrap import MPI

if MPI:
    filename = 'data_0.dmp'
else:
    filename = 'data.dmp'


def extract_all_vars(name):
    """ Reads in the file given in name and extracts all variables."""

    file = open(name)
    data = {}
    record_flag = False
    for line in file:

        if line.startswith('Unknowns'):
            record_flag = True
            continue
        elif line.startswith('Resids:'):
            record_flag = False
            continue

        if record_flag is True:
            key, value = line.split(':')
            key = key.lstrip()
            if key not in data:
                data[key] = []
            data[key].append(float(value.lstrip().replace('\n', '')))

    return data


data = extract_all_vars(filename)
n_point = (len(data) - 1)/5

X = data['obj.val']
X = [-val for val in X]
ncase = len(X)

Y = []
Z = []
for ic in range(ncase):
    c1 = c2 = c3 = c4 = c5 = 0
    for ip in range(n_point):
        c1 += data['pt%d_con1.val' % ip][ic]
        c2 += data['pt%d_con2.val' % ip][ic]
        c3 += data['pt%d_con3.val' % ip][ic]
        c4 += data['pt%d_con4.val' % ip][ic]
        c5 += data['pt%d_con5.val' % ip][ic]

    feasible = [c1, c2, c3, c4, c5]

    Y.append(sum(feasible))
    Z.append(feasible)

#for case in cases:
    #data = [ case['pt' + str(i) + '.Data'][0][1499] for i in xrange(6) ]
    #sumdata = sum([float(i) for i in data if i])

    #c1 = [get_constraint_value_from_case( cds, case, "pt" + str(i) + ".ConCh <= 0") for i in xrange(6)]
    #c2 = [get_constraint_value_from_case( cds, case, "pt" + str(i) + ".ConDs <= 0") for i in xrange(6)]
    #c3 = [get_constraint_value_from_case( cds, case, "pt" + str(i) + ".ConS0 <= 0") for i in xrange(6)]
    #c4 = [get_constraint_value_from_case( cds, case, "pt" + str(i) + ".ConS1 <= 0") for i in xrange(6)]
    #c5 = [get_constraint_value_from_case( cds, case, "pt" + str(i) + ".SOC[0][0] = pt" + str(i) + ".SOC[0][-1]") for i in xrange(6)]


    #c1_f = sum([float(i) for i in c1 if i])
    #c2_f = sum([float(i) for i in c2 if i])
    #c3_f = sum([float(i) for i in c3 if i])
    #c4_f = sum([float(i) for i in c4 if i])
    #c5_f = sum([float(i) for i in c5 if i])

    #feasible = [c1_f, c2_f,  c3_f, c4_f, c5_f]

    #X.append(sumdata), Y.append(sum(feasible)), Z.append(feasible)

    #pcom.append([float(case["pt5.CP_gamma"][i])for i in xrange(300)])

    ## print sumdata, sum(feasible), max(feasible) #,[ '%.1f' % i for i in
    ## feasible]
    #print sumdata

#pylab.figure()
#pylab.plot(pcom[-1])

Z = np.array(Z)
if not len(Z):
    print "no data yet..."
    quit()
pylab.figure()
pylab.subplot(311)
pylab.title("total data")
pylab.plot(X, 'b')
pylab.plot([0, len(X)], [3e4, 3e4], 'k--', marker="o")
pylab.subplot(312)
pylab.title("Sum of Constraints")
pylab.plot([0, len(Y)], [0, 0], 'k--', marker="o")
pylab.plot(Y, 'k')
pylab.subplot(313)
pylab.title("Max of Constraints")
pylab.plot([0, len(Z)], [0, 0], 'k--')
pylab.plot(Z[:, 0], marker="o", label="c1")
pylab.plot(Z[:, 1], marker="o", label="c2")
pylab.plot(Z[:, 2], marker="o", label="c3")
pylab.plot(Z[:, 3], marker="o", label="c4")
pylab.plot(Z[:, 4], marker="o", label="c5")
pylab.legend(loc="best")

pylab.show()
