#!/usr/bin/env python
# -*- coding: utf-8 -*-


from selenium import webdriver
import time
import json
import datetime
import sys
import math

reload(sys)
sys.setdefaultencoding('utf8')

driver = webdriver.PhantomJS()

try:
    pl_link = sys.argv[1]
except:
    print "Run the script like: python manualSave.py <url_of_playlist>"
    sys.exit()

driver.get(pl_link)

plname = driver.find_element_by_xpath("//h1[@class='pl-header-title']").text

print "Starting to backup the playlist '" + plname + "'..."

output = {}
output['Videos'] = {}
number_of_videos = 0
number_of_deleted_videos = 0
totalseconds = 0.0

keep_lookin = True

while keep_lookin:

    # ele = driver.find_elements_by_xpath("//a[contains(@class, 'pl-video-title-link')]")
    ele = driver.find_elements_by_xpath(
        "//tr[contains(@class, 'yt-uix-tile')]")

    for e in ele[number_of_videos:]:
        ee = e.find_element_by_xpath(
            ".//a[contains(@class, 'pl-video-title-link')]")

        title = ee.text.encode('utf8')
        print "Video " + str(number_of_videos+1) + ": " + title + ".",

        output['Videos'][number_of_videos] = {}
        output['Videos'][number_of_videos]['Title'] = title
        output['Videos'][number_of_videos][
            'Link'] = ee.get_attribute('href').split('&')[0]

        try:
            t = e.find_element_by_xpath(
                ".//div[contains(@class, 'timestamp')]").text
        except:
            print ''
            pass
        else:
            print " " + t
            output['Videos'][number_of_videos]['Duration'] = t
            spl_t = t.split(':')
            if len(spl_t) is 2:
                totalseconds += float(spl_t[-2])*60 + float(spl_t[-1])
            elif len(spl_t) is 3:
                totalseconds += float(spl_t[-3])*3600 + \
                    float(spl_t[-2])*60 + float(spl_t[-1])

        number_of_videos += 1

    buto = driver.find_elements_by_xpath(
        "//span[contains(@class,'load-more-text')]")

    try:
        buto[0].click()
    except:
        print "Reached end of playlist with " + str(number_of_videos) + " videos."
        keep_lookin = False
    else:
        print "Loading more..."
        time.sleep(5)

for k, v in output['Videos'].iteritems():
    if "Vídeo suprimit" in v['Title']:
        number_of_deleted_videos += 1
        output['Videos'][k]["Google Results"] = []
        video_id = v['Link'].split('=')[-1]
        query = "https://www.google.com/search?q=" + video_id

        driver.get(query)
        results = driver.find_elements_by_xpath("//div[@class='g']")

        print "The video with id '" + video_id + "' was deleted. Here are some Google results that might help:"

        for r in results:

            try:
                possible = {}
                name_link = r.find_element_by_xpath("./h3[@class='r']")
                possible['Result Name'] = name_link.text
                print "\t- " + name_link.text
                possible['Result Link'] = name_link.find_element_by_xpath(".//a").get_attribute('href').split('q=')[1].split('&sa')[0]
                
                output['Videos'][k]["Google Results"].append(possible)
            except:
                pass

hours = totalseconds/3600.0
minutes = ((hours-math.floor(hours))*3600.0)/60.0
seconds = (minutes-math.floor(minutes))*60.0

duration_str = str(int(math.floor(hours))) + ':' + \
    str(int(math.floor(minutes))) + ':' + str(int(math.floor(seconds)))

print "The playlist '" + plname + "'' of " + str(number_of_videos) + " videos is " + duration_str + " long."

output['Info'] = {}
output['Info']['Duration'] = duration_str
output['Info']['Playlist Name'] = plname
output['Info']['Number of videos'] = number_of_videos
output['Info']['Deleted'] = number_of_deleted_videos

date_string = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M")

with open(plname+"_backup_"+date_string+".json", 'w') as f:
    json.dump(output, f, sort_keys=True, indent=4,
              separators=(',', ': '), ensure_ascii=False)

driver.quit()
