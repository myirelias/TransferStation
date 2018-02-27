import time


def tool_data_format(self, data):
    """
    对数据进行格式化，目前只接受由dict类型组成的list的数据
    :param data: 一个或多个dict组成的list
    :return: 格式化后的数据
    """
    all_name = set([])
    for each in data:
        all_name.add(each.get('dealer_name'))

    for one in all_name:
        onelist = []
        for each in data:
            if each.get('dealer_name') == one:
                onelist.append(each)

        typename = set([])
        for eveyone in onelist:
            tasktype = eveyone.get('tasktype')
            typename.add(tasktype)

        for eachtype in typename:
            typelist = []
            for eveyone in onelist:
                if eveyone.get('tasktype') == eachtype:
                    typelist.append(eveyone.get('info'))
            save_name = one, ':\n', eachtype.strip(), '\n'
            for each in typelist:
                save_info = '\t\t', each.strip(), '\n'


if __name__ == '__main__':
    tool_data_format()
