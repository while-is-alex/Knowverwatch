import re


class Stats:
    def split_camel_case(self, str):
        words = [[str[0]]]

        for c in str[1:]:
            if words[-1][-1].islower() and c.isupper():
                words.append(list(c))
            else:
                words[-1].append(c)

        words = [''.join(word) for word in words]
        resulting_string = ' '.join(words).title()
        return resulting_string

    def format_details(self, hero_name, stats_dictionary):
        keys = stats_dictionary.keys()
        hero_stats = []
        for key in keys:
            statistic = {'name': self.split_camel_case(key), 'value': int(stats_dictionary[key])}
            hero_stats.append(statistic)

        if len(hero_stats) > 3:
            hero_details = (hero_name.title(), hero_stats)
            return hero_details
