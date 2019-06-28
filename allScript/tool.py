# coding=utf-8
"""
工具包
"""
import os


class Tools:
    """
    各种工具
    """

    @staticmethod
    def tools_city_dict(city_list=None):
        """
        将城市数据转换成三级字典
        :return:
        """
        try:
            allcitys = list(con for con in open(os.path.abspath('DATA/city_list_total.txt'), 'r', encoding='utf-8'))
        except Exception as e:
            raise Exception(e)
        city_list = list(con for con in open(os.path.abspath('DATA/file_city_list.txt'), 'r', encoding='utf-8'))
        current_dict = {}
        now_list = []
        cu_list = []
        for each in city_list:
            cityname = each.strip().split('\u0001')[0]
            cityurl = each.strip().split('\u0001')[1]
            for every in allcitys:
                current = every.strip().replace('\ufeff', '').split('\u0001')
                prov = [current[0], current[1]]
                city = [current[2], current[3]]
                area = [current[5], current[4]]
                if cityname in city:
                    if not current_dict.get(prov[0]):
                        current_dict[prov[0]] = {city[0]: {'': cityurl}}
                    else:
                        current_dict[prov[0]][city[0]] = {'': cityurl}
                    break
                elif cityname in area:
                    if not current_dict.get(prov[0]):
                        if not current_dict.get(prov[0], {}).get(city[0]):
                            current_dict[prov[0]] = {city[0]: {area[0]: cityurl}}
                        else:
                            current_dict[prov[0]][city[0]] = {area[0]: cityurl}
                    break
                elif cityname in prov:
                    current_dict[prov[0]] = {'': {'': cityurl}}
                    break
                # elif cityname in area:
                #     current_dict[prov][city][area] = cityurl
                #     break
                else:
                    continue
        with open('./DATA/file_city_dict.txt', 'w', encoding='utf-8') as f:
            f.write(str(current_dict))
        print(current_dict)


        each = '海南州'
        for eachone in city_list:
            cityname = eachone.strip().split('\u0001')[0]
            cityurl = eachone.strip().split('\u0001')[1]
            if each == cityname:
                current_dict['青海省'][each] = {'': cityurl}
                break


if __name__ == '__main__':
    pro = Tools()
    pro.tools_city_dict()

