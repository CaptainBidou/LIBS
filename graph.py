import matplotlib.pyplot as plt
class Graph:
    def __init__(self,timeTab, socTab, socEstimator, voltageTab, currentTab, gTab,name):
        # name ends by .txt so we remove it
        name = name[:-4]
        # name starts by TestHard/ so we remove it
        name = name[9:]


        rmse = 0
        ame = 0
        mae = 0
        for i in range(len(socTab)):
            rmse += ((socTab[i] - socEstimator[i])/socTab[i])**2
            ame += abs((socTab[i] - socEstimator[i])/socTab[i])
            if(abs((socTab[i] - socEstimator[i])/socTab[i]) > mae):
                mae = abs((socTab[i] - socEstimator[i])/socTab[i])
        rmse = 100 * (rmse/len(socTab))**0.5
        ame = 100 * (ame/len(socTab))
        mae = 100 * mae


        fig2, ax2 = plt.subplots()
        ax2.plot(timeTab, socTab, label='soc')
        ax2.plot(timeTab, socEstimator, label='socEstimator')
        plt.xlabel('time')
        plt.ylabel('soc')
        # the ordonnate of the graph have to show only 0 to 1 values
        plt.ylim(0, 1.1)
        plt.title(name)
        # put it in the middle of the graph
        plt.figtext(0.5, 0.25, 'RMSE = ' + str(rmse) + ' %', wrap=True, horizontalalignment='center', fontsize=12)
        plt.figtext(0.5, 0.2, 'AME = ' + str(ame) + ' %', wrap=True, horizontalalignment='center', fontsize=12)
        plt.figtext(0.5, 0.15, 'MAE = ' + str(mae) + ' %', wrap=True, horizontalalignment='center', fontsize=12)
        ax2.legend()
        plt.show()
        # plt.savefig(name + 'soc.png')

        rmse = 0
        ame = 0
        mae = 0
        for i in range(len(voltageTab)):
            rmse += ((voltageTab[i] - gTab[i]) / voltageTab[i]) ** 2
            ame += abs((voltageTab[i] - gTab[i]) / voltageTab[i])
            if (abs((voltageTab[i] - gTab[i]) / voltageTab[i]) > mae):
                mae = abs((voltageTab[i] - gTab[i]) / voltageTab[i])
        rmse = 100 * (rmse / len(voltageTab)) ** 0.5
        ame = 100 * (ame / len(voltageTab))
        mae = 100 * mae


        fig, ax = plt.subplots()
        ax.plot(timeTab, voltageTab, label='voltage')
        ax.plot(timeTab, currentTab, label='current')
        ax.plot(timeTab, gTab, label='g')
        plt.xlabel('time')
        plt.ylabel('voltage/current')
        plt.ylim(0, 5)
        plt.title(name)
        # plt.figtext(0.5, 0.01, 'RMSE = ' + str(rmse) + ' %', wrap=True, horizontalalignment='center', fontsize=12)
        # plt.figtext(0.5, 0.05, 'AME = ' + str(ame) + ' %', wrap=True, horizontalalignment='center', fontsize=12)
        # plt.figtext(0.5, 0.09, 'MAE = ' + str(mae) + ' %', wrap=True, horizontalalignment='center', fontsize=12)
        ax.legend()
        plt.show()
        # plt.savefig(name + 'voltage.png')

