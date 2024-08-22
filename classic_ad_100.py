import markdown
import streamlit as st
from streamlit_player import st_player


def ad():
    st.markdown("""
    1999年《广告时代》（AA)杂志评选出20世纪最成功的百強广告活动，入选广告需达到或通过以下三条标准之一：

        A、是否构成了广告或社会流行文化的分水岭；
        B、是否促进了新品类的形成或帮助客户品牌成为其所属行业的龙头；
        C、是否令人难以忘怀。


    **榜单排名如下（品牌名称-广告语-广告代理商及时间）：**

    1. 大众甲壳虫汽车(Volkswagen)，"think small"（从小处着眼），DDB，1959
    ![Think Small advertising campaign](https://www.sourcetype.com/images/ok_BLUE_2.png?w=1600)

    2. 可口可乐(Coca-Cola)，\"The pause that refreshes\" （享受清新一刻），
    D\'Arcy Co. ，1929

    3. 万宝路(Marlboro)，"The Marlboro Man"(万宝路牛仔)， Leo Burnett Co.

    ，1955

    4. 耐克(Nike)，**"** Just Do It **" (**尽管去做)， Wieden & Kennedy
    ，1988

    5. 麦当劳(McDonald\'s)，\"You deserve a break today\"
    (今天你该休息了)，Needham, Harper & Steers，1971

    6. 戴比尔斯(DeBeers)，\"A diamond is forever\"
    (钻石恒久远，一颗永流传)， N.W. Ayer & Son ，1948

    7. 绝对伏特加(Absolut Vodka)，"The Absolut
    Bottle"（绝对伏特加酒瓶），TBWA，1981

    8. 米勒淡啤(Miller Lite beer)，\"Tastes great, less filling\"
    （喝不够的味道）， McCann-Erickson Worldwide ，1974

    9. 伊卡璐染发水(Clairol)：\"Does she...or doesn\'t she?\"
    （她染了？还是没染？），FCB，1957

    10. 安飞士出租车公司(Avis)，\"We try harder\" （我们更努力），DDB，1963

    11. 联邦快递(Federal Express)，\"Fast talker\" (快腿当差)， Ally &
    Gargano ，1982

    12. 苹果电脑(Apple Computer)，"1984"，Chiat/Day，1984

    13. Alka-Seltzer药品(Alka-Seltzer)， "Various ads" (广告万花筒)，Jack
    Tinker & Partners；DDB；Wells Rich, Greene，20世纪60、70年代

    14. 百事可乐(Pepsi-Cola)，\"Pepsi-Cola hits the spot\"
    （百事，就是这个口味），Newell-Emmett Co.，20世纪40年代

    15. 麦斯威尔咖啡(Maxwell House)，\"Good to the last drop\"
    (滴滴香浓，意犹未尽)， Ogilvy, Benson & Mather ，1959

    16. 宝洁象牙皂(Ivory Soap)，\"99 and 44/100% Pure\" （99.44％的纯净），
    Procter & Gamble Co. ，1882

    17. 美国运通(American Express)，\"Do you know me?\" （你知道我吗？），
    Ogilvy & Mather ，1975

    18. 美国陆军(U.S. Army)，\"Be all that you can be\"
    （成为最好的自己）， N.W. Ayer & Son ，1981

    19. 安乃静解热去痛片(Anacin)，\"Fast, fast, fast relief\"
    (快、快、快速见效)， Ted Bates & Co. ，1952

    20. 滚石乐队(Rolling Stone)，\"Perception. Reality.\"
    （真实的感觉），FMR（Fallon McElligott Rice），1985 
    21.
    百事可乐(Pepsi-Cola)，\"The Pepsi generation\"
    (新一代的选择)，BBDO，1964

    22. 哈斯维衬衫(Hathaway Shirts)，\"The man in the Hathaway shirt\"
    （穿哈斯维的男人），Hewitt, Ogilvy, Benson & Mather ，1951

    23. 博马剃须刀(Burma-Shave)，" Roadside signs in verse " （路边的诗句牌
    ），Allen Odell，1925

    注：Burma-Shave公司在当时采用了一种独特的广告方式，他们将广告内容分成多个简短的诗句，逐个放置在沿路的标牌上，形成连贯的广告信息。这些标牌以幽默和押韵的形式传递广告信息，成为了当时非常受欢迎和具有影响力的广告形式。

    24. 美国汉堡王(Burger King)，\"Have it your way\"
    （我选我味），BBDO，1973

    25. 坎贝尔浓汤(Campbell Soup)，\"Mmm mm good\"
    （啧嘖,真好味！），BDO，20世纪30年代

    26. 美国林业总署(U.S. Forest Service)， Smokey the Bear/\"Only you can
    prevent forest fires\" （护林熊/"只有你能防止森林火灾"），Advertising
    Council/FCB

    27. 百威啤酒(Budweiser)，\"This Bud\'s for you\" （为你准备的百威），
    D\'Arcy Masius Benton & Bowles ，20世纪70年代

    28. 媚登峰内衣(Maidenform)，\"I dreamed I went shopping in my
    Maidenform bra\" （真想穿媚登峰内衣去逛街）， Norman, Craig &
    Kunnel，1949

    29. 胜利唱机公司(Victor Talking Machine)，\"His master\'s voice\"
    （主人之声），Francis Barraud，1901

    30.Jordan汽车(Jordan Motor Car Co.)，\"Somewhere west of Laramie\"
    （拉勒米以西的某处" ，Edward S. (Ned) Jordan，1923

    31. Woodbury香皂(Woodbury Soap)，\"The skin you love to touch\"
    （你爱触摸的肌肤），JWT，1911

    32. Benson & Hedges 100s香烟，\"The disadvantages\"（有害），Wells,
    Rich, Greene，20世纪60年代

    33. 国民饼干(National Biscuit )，"Uneeda Biscuits\' Boy in Boots"（
    Uneeda饼干的穿靴男孩 ）， N.W. Ayer & Son ，1899

    注： 这是Uneeda Biscuits品牌饼干的形象广告，塑造了一个渴望 Uneeda
    Biscuits饼干的穿靴子小男孩，用以传达产品的亲和力和吸引力。

    34. 劲量电池(Energizer)，"The Energizer
    Bunny"（劲量兔子），Chiat/Day，1989

    35. 莫顿食盐（Morton Salt），\"When it rains it pours\"
    （下雨时，它会倾泻 ）， N.W. Ayer & Son ，1912

    注：这个广告语传达了Morton盐在潮湿条件下仍然能保持流动性的特点，突出了其抗结块的卖点。

    36. 夏奈尔香水(Chanel)，\"Share the fantasy\" （梦幻分享），DDB，1979

    37. 通用土星汽车(Saturn)，\"A different kind of company, A different
    kind of car.\" （不一样的公司，不一样的汽车），Hal Riney & Partners
    ，1989

    38. 佳洁士牙膏(Crest toothpaste)，\"Look, Ma! No cavities!\"
    （妈妈，看，我没有蛀牙！），Benton & Bowles ，1958

    39. M巧克力(M&Ms)，\"Melts in your mouth, not in your hands\"
    （只溶在口，不溶在手）， Ted Bates & Co. ，1954

    40. 天美时手表(Timex)，\"Takes a licking and keeps on ticking\"
    （经得摔打，依旧准确 ），W.B. Doner & Co & predecessor公司，20世纪50年代

    41. 雪佛兰汽车(Chevrolet)，\"See the USA in your Chevrolet\"
    （乘雪佛兰逛美国），Campbell-Ewald，20世纪50年代

    42. CK内衣(Calvin Klein)，\"Know what comes between me and my Calvins?
    Nothing!\" （我和Calvin 亲密无间）

    43. 里根竞选总统广告(Reagan for President)，\"It\'s morning again in
    America\" （美国迎来又一个清晨），Tuesday Team，1984

    44. 云丝顿香烟(Winston cigarettes)，\"Winston tastes good--like a
    cigarette should\" （云丝顿，香烟该有的味道），1954

    45. 美国音乐学校(U.S. School of Music)，\"They laughed when I sat down
    at the piano, but when I started to play!\"
    （我开始演奏时，众人目瞪口呆！）， Ruthrauff & Ryan，1925

    46. 骆驼香烟(Camel cigarettes)，\"I\'d walk a mile for a Camel\"
    （只为---支骆驼烟，我宁愿走一英里）， N. W. Ayer & Son ，1921

    47. 温迪汉堡包(Wendy\'s)，\"Where\'s the beef?\"
    （牛肉在哪里？），Dancer-Fitzgerald-Sample，1984

    48. 李斯特林漱口水（Listerine），\"Always a bridesmaid, but never a
    bride\"（总是伴娘，从未新娘），Lambert & Feasley，1923

    注：
    这个广告语旨在突出使用Listerine可以避免因为口臭而错失机会，暗示使用者可能从伴娘成为新娘。

    49. 卡迪拉克(Cadillac)，\"The penalty of leadership\"\
    （出人头地的代价），MacManus, John & Adams，1915

    50. 让美国美丽组织（Keep America Beautiful），\"Crying Indian\"
    （哭泣的印第安人），Advertising Council/Marstellar Inc.，1971

    51. 宝洁Charmin卫生纸，\"Please don\'t squeeze the Charmin\"
    （请别冷淡了Charmin），Benton & Bowles，1964

    注： Charmin 即 迷人的。

    52. Wheaties麦片(Wheaties)，\"Breakfast of champions\"

    （冠军的早餐），Blackett-Sample-Hummert，20世纪30年代

    53. 可口可乐(Coca-Cola)，\"It\'s the real thing\" （这是真的），
    McCann-Erickson ，1970

    54. 灰狗巴士(Greyhound)，\"It\'s such a comfort to take the bus and
    leave the driving to us\" （有坐车之乐，无开车之累）， Grey Advertising
    ，1957

    55. 家乐氏西式爆米花（Kellogg\'s Rice Krispies），\"Snap! Crackle! and
    Pop!\" （咬一口，咔嚓脆）， Leo Burnett Co. ，20世纪40年代

    56. 宝丽来拍立得(Polaroid)，\"It\'s so
    simple\"（就是这么简单），DDB，1977

    57. 吉列剃须刀(Gillette)，\"Look sharp, feel sharp\"
    （看似锋利，确实锋利），BBDO，20世纪40年代

    58. 莱唯斯雷面包(Levy\'s Rye Bread)，\"You don\'t have to be Jewish to
    love Levy\'s Rye Bread\" （不是犹太人也照样喜欢莱唯斯雷面包），DDB，1949

    59. Pepsodent增白牙膏，\"You\'ll wonder where the yellow went\"
    （奇怪，黄斑哪去了），FCB，1956

    60. Lucky Strike香烟，\"Reach for a Lucky instead of a sweet\"
    （好运胜过甜蜜），Lord & Thomas，20世纪20年代

    61. 七喜汽水(7 UP)，\"The Uncola\" （并非可乐），JWT，20世纪70年代

    62. 威斯克洗衣粉 (Wisk detergent)，\"Ring around the collar\"
    （洁淨领渍），BBDO，1968

    63. 西梅精华(Sunsweet Prunes)，\"Today the pits, tomorrow the
    wrinkles\" (今时之斑点，明日出皱纹），Freberg Ltd.，20世纪70年代

    64. Life 麦片(Life cerea)，"Hey, Mikey"（嘿，米奇），DDB，1972

    65. 赫兹租车公司(Hertz)，\"Let Hertz put you in the driver\'s seat\"
    （让赫兹把你带到驾驶座上 ），Norman, Craig & Kummel，1961

    66. Foster Grant太阳镜，\"Who\'s that behind those Foster Grants?\"
    （戴Foster Grants太阳镜的是谁？）,Geer, Dubois，1965

    67. 柏杜鸡（Perdue chicken），\"It takes a tough man to make tender
    chicken\" （硬汉也能做出鲜嫩鸡肉）， Scali, McCabe, Sloves , 1971

    68. 贺曼卡片(Hallmark)，\"When you care enough to send the very best\"
    （如果你真的在乎，就寄最好的贺卡），FCB，20世纪30年代

    69. Springmaid 床单，\"A buck well spent\" （物有所值），
    In-house，1948

    70. Queensboro 集团，" Jackson Heights Apartment
    Homes"（杰克逊高地公寓之家），WEAF, NYC，20世纪20年代

    71. 施坦威钢琴（Steinway & Sons）, \"The instrument of the immortals\"
    （不朽的乐器）, N.W. Ayer & Sons , 1919

    72. Levi's牛仔裤，\"501 Blues\" （501款蓝色牛仔裤），FCB，1984

    73. 黑玉蝠貂 (Blackglama-Great Lakes Mink)，\"What becomes a legend
    most?\" （什么最适合传奇？） ， Jane Trahey Associates ，20世纪60年代

    注：
    这个广告语以神秘和优雅的方式强调了Blackglama水貂皮草的高贵和经典地位。

    74. 蓝仙姑葡萄酒（Blue Nun），"Stiller & Meara campaign"
    （斯蒂勒与米拉广告喜剧），Della Famina, Travisano & Partners，
    20世纪70年代

    注： 这个广告活动以喜剧演员夫妇Jerry Stiller和Anne
    Meara的幽默表演著称，用以宣传Blue Nun葡萄酒。

    75. 哈姆啤酒（Hamm\'s beer），\"From the Land of Sky Blue Waters\"
    "源自蓝天水乡"，Campbell-Mithun，20世纪50年代

    76. Quaker Puffed麦片，"Shot from guns " （枪炮爆米花 ），Lord &
    Thomas，20世纪20年代

    注： 这个广告强调了Quaker
    Puffed谷物采用高压加热的制作工艺，使其谷物膨化如同从枪炮中射出一样。

    77. ESPN体育频道，\"This is SportsCenter\" "这里是体育中心"， Wieden &
    Kennedy， 1995

    78. Molson啤酒，" Laughing Couple"（欢笑的一对），Moving & Talking
    Picture Co.，20世纪80年代

    79. 加州乳品加工协会(California Milk Processor Board)，\"Got Milk?\"
    （喝牛奶了吗？），1993

    80. 美国电话电报公司(AT&T)，\"Reach out and touch someone\"
    "伸出臂膀，拥抱世界"， N.W. Ayer & Sons （艾尔父子广告），1979

    81. 百洁霜(Brylcreem)，\"A little dab\'ll do ya\" （每次只需一点点），
    Kenyon & Eckhardt ，20世纪50年代

    82. 嘉灵黑啤酒(Carling Black Label beer)，\"Hey Mabel, Black Label!\"
    "嗨！梅布尔，嘉灵黑牌"， Lang, Fisher & Stashower ，20世纪40年代

    83. 五十铃 (Isuzu) ，\"Lying Joe Isuzu\" （说谎的乔•五十铃）， Della
    Famina, Travisano & Partners ，20世纪80年代

    84. 宝马(BMW)，\"The ultimate driving machine\" "终极驾驶机器"，
    Ammirati & Puris ，1975年

    85. 德士古公司(Texaco)， \"You can trust your car to the men who wear
    the star\"

    "你的车可托付给佩戴星标的人"， Benton & Bowles ，20世纪40年代

    86. 可口可乐 (Coca-Cola )，\"Always\" "永远的可口可乐"， Creative
    Artists Agency ，1993年

    87. 施乐(Xerox)，\"It\'s a miracle\" （它是个奇迹）， Needham, Harper &
    Steers ，1975年

    88. 巴特尔•杰默斯葡萄酒(Bartles & Jaymes)，\"Frank and Ed\"
    （弗兰克和埃德）， Hal Riney & Partners ，1985年

    89. 达能酸奶(Dannon Yogurt)，\"Old People in Russia\" "俄罗斯的老人"，
    Marstellar Inc. ，20世纪70年代

    90. 沃尔沃(Volvo)，" Average life of a car in
    Sweden""车在瑞典的平均寿命"， Scali, McCabe, Sloves ，20世纪60年代

    91. 6号汽车旅馆(Motel 6)，\"We\'ll leave a light on for you\"
    "始终为你亮灯"， Richards Group ，1988年

    92.果冻(Jell-O)，"Bill Cosby with kids"（比尔•考斯比和孩子们）， Young &
    Rubicam ，1975年

    93. IBM，"Chaplin\'s Little Tramp character""小丑卓别林"， Lord,
    Geller, Federico, EinsteinLord, Geller, Federico, Einstein ，1982年

    94. 美国旅行者箱包(American Tourister)，"The
    Gorilla"（大猩猩），DDB，20世纪60年代晚期

    95. 赞宝除臭剂(Right Guard)，\"Medecine Cabinet\"
    （药柜），BBDO，20世纪60年代

    96. 梅宝(Maypo)，\"I want my Maypo\" （我要我的梅宝）， Fletcher,
    Calkins & Holden ，20世纪60年代

    97. 百服宁(Bufferin)，" Pounding heartbeat"（強有力的心跳）， Young &
    Rubicam ，1960年

    98. 箭牌衬衫(Arrow Shirts)，\"My friend, Joe Holmes, is now a horse\"
    （我的朋友乔•霍尔姆斯，（穿箭牌）如同马）， Young & Rubicam ，1938年

    99. 扬•罗必凯自身广告(Young & Rubicam)，\"Impact\" （震撼）， Young &
    Rubicam ，1930年

    100. 林登•约翰逊竞选美国总统(Lyndon Johnson for Presiden)，\"Daisy\"
    （雏菊），DDB，1964年

    以上入选的广告20世纪百佳广告，每一个都有其精彩的故事。单光凭一句简单的广告语，不知其背景和场景，实难以理解这些广告何以伟大广告的奧秘。让我们以最后一条入选广告为例略作说明：

    林登·约翰逊（Lyndon B.
    Johnson）是美国历史上的一位总统，他在1963年至1969年间任职。1964年他竞选总统期间，出现了一则非常有名称为\"Daisy\"的广告。

    这则广告最初于1964年9月7日播放，是约翰逊竞选团队制作的。广告的主要内容是一个可爱的小女孩在一个花园里，她正在数着雏菊的花瓣。当她数到"9"时，画面切换到一个导弹发射的场景，接着是一个巨大的爆炸蘑菇云。广告结束时，有一个声音在背景说：\"这次选举，请投票给约翰逊。因为你的生活和你的孩子的生活取决于它，每一天都可能下（蘑菇）雨。\"

    \"Daisy\"广告的目的是通过暗示共和党候选人巴里·戈德沃特（Barry
    Goldwater）对核武器使用的立场，表达对他激进的军事政策的担忧。这则广告的情感强烈，利用了对核战争的普遍恐惧，试图让选民相信如果选错了总统，可能会导致灾难性的后果。

    这则广告引起了很大的争议，一些人批评它是在利用恐惧来获得选民的支持，而其他人则认为它成功地传达了对戈德沃特的担忧。不管怎样，这则\"Daisy\"广告在美国政治广告的历史上留下了深远的影响，被认为是一种将情感与政治联系起来的典型例子。

    来源：该榜单英文源于广告时代（AA），

    Ad Age Advertising Century: Top 100 Campaigns[EB/OL]//Ad Age.
    (1999-03-29)[2023-12-21].
    https://adage.com/article/special-report-the-advertising-century/ad-age-advertising-century-top-100-advertising-campaigns/140150.

                """)


def ad_1():
    st.markdown("""
    1. 大众甲壳虫汽车(Volkswagen)，"think small"（从小处着眼），DDB，1959
    """
    )
    st.image(
        "https://www.aaaa.org/wp-content/uploads/2017/03/1959_ThinkSmall_400.jpg",
        width=600,  # Manually Adjust the width of the image as per requirement
    )

    # Additional text or widgets can be added here


def ad_2():
    st.markdown("""
    2. 可口可乐(Coca-Cola)，\"The pause that refreshes\" （享受清新一刻），
    D\'Arcy Co. ，1929
    """
    )
    st.image(
        "https://susanascher.com/wp-content/uploads/2014/10/pausecoke.jpg",
        width=600,  # Manually Adjust the width of the image as per requirement
    )

    # Additional text or widgets can be added here


def ad_3():
    st.markdown("""
       3. 万宝路(Marlboro)，"The Marlboro Man"(万宝路牛仔)， Leo Burnett Co. ，1955

    """
    )
    st.image(
        "https://cdn-images-1.medium.com/v2/resize:fit:401/1*LqszYoloTnOdviaSavNzvQ.jpeg",
        width=600,  # Manually Adjust the width of the image as per requirement
    )

    # Additional text or widgets can be added here


def ad_4():
    st.markdown("""
        4. 耐克(Nike)，**"** Just Do It **" (**尽管去做)， Wieden & Kennedy
    ，1988

    """
    )
    st.video('https://youtu.be/0yO7xLAGugQ')
    # Additional text or widgets can be added here


def ad_5():
    st.markdown("""
        5. 麦当劳(McDonald\'s)，\"You deserve a break today\"
    (今天你该休息了)，Needham, Harper & Steers，1971

    """
    )
    st.video('https://youtu.be/-tQPd8-BCvA')
    # Additional text or widgets can be added here


def ad_6():
    st.markdown("""
            6. 戴比尔斯(DeBeers)，\"A diamond is forever\"
    (钻石恒久远，一颗永流传)， N.W. Ayer & Son ，1948
    """
    )
    st.image('https://www.aaaa.org/wp-content/uploads/2017/03/1948_ADiamondIsForever_668.jpg',width=600)
    # Additional text or widgets can be added here


def ad_7():
    st.markdown("""
7. 绝对伏特加(Absolut Vodka)，"The Absolut
    Bottle"（绝对伏特加酒瓶），TBWA，1981
    """
    )
    # st.image('https://www.aaaa.org/wp-content/uploads/2017/03/1948_ADiamondIsForever_668.jpg',width=600)
    st.video('https://youtu.be/O5qnrLw07gc')
    # Additional text or widgets can be added here



def ad_8():
    st.markdown("""
 8. 米勒淡啤(Miller Lite beer)，\"Tastes great, less filling\"
    （喝不够的味道）， McCann-Erickson Worldwide ，1974

    """
    )
    # st.image('https://www.aaaa.org/wp-content/uploads/2017/03/1948_ADiamondIsForever_668.jpg',width=600)
    st.video('https://youtu.be/argdPEmD9bI')
    # Additional text or widgets can be added here

def ad_9():
    st.markdown("""
 9. 伊卡璐染发水(Clairol)：\"Does she...or doesn\'t she?\"
    （她染了？还是没染？），FCB，1957

    """
    )
    # st.image('https://www.aaaa.org/wp-content/uploads/2017/03/1948_ADiamondIsForever_668.jpg',width=600)
    st.video('https://youtu.be/GXkzl2I5CH8')
    # Additional text or widgets can be added here


def ad_10():
    st.markdown("""
10. 安飞士出租车公司(Avis)，\"We try harder\" （我们更努力），DDB，1963

    """
    )
    # st.image('https://www.aaaa.org/wp-content/uploads/2017/03/1948_ADiamondIsForever_668.jpg',width=600)
    st.video('https://youtu.be/8gMsusVaLng')
    # Additional text or widgets can be added here



def ad_11():
    st.markdown("""
11. 联邦快递(Federal Express)，\"Fast talker\" (快腿当差)， Ally &
    Gargano ，1982

    """
    )
    # st.image('https://www.aaaa.org/wp-content/uploads/2017/03/1948_ADiamondIsForever_668.jpg',width=600)
    st.video('https://youtu.be/CUL-qJvQc8A')
    # Additional text or widgets can be added here



def ad_12():
    st.markdown("""
12. 苹果电脑(Apple Computer)，"1984"，Chiat/Day，1984

    """
    )
    # st.image('https://www.aaaa.org/wp-content/uploads/2017/03/1948_ADiamondIsForever_668.jpg',width=600)
    st.video('https://youtu.be/VtvjbmoDx-I')
    # Additional text or widgets can be added here


def ad_13():
    st.markdown("""
  13. Alka-Seltzer药品(Alka-Seltzer)， "Various ads" (广告万花筒)，Jack
    Tinker & Partners；DDB；Wells Rich, Greene，20世纪60、70年代

    """
    )
    # st.image('https://images.app.goo.gl/hVVhGwZQW7iGMQ836',width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://vimeo.com/191873873')
    # Additional text or widgets can be added here


def ad_14():
    st.markdown("""
14. 百事可乐(Pepsi-Cola)，\"Pepsi-Cola hits the spot\"
    （百事，就是这个口味），Newell-Emmett Co.，20世纪40年代

    """
    )
    # st.image('https://images.app.goo.gl/hVVhGwZQW7iGMQ836',width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/2gnlKBIL-vo')
    # Additional text or widgets can be added here



def ad_15():
    st.markdown("""
15. 麦斯威尔咖啡(Maxwell House)，\"Good to the last drop\"
    (滴滴香浓，意犹未尽)， Ogilvy, Benson & Mather ，1959
    """
    )
    # st.image('https://images.app.goo.gl/hVVhGwZQW7iGMQ836',width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/djj5GzRQD0o')
    # Additional text or widgets can be added here


def ad_16():
    st.markdown("""
16. 宝洁象牙皂(Ivory Soap)，\"99 and 44/100% Pure\" （99.44％的纯净），
    Procter & Gamble Co. ，1882

    """
    )
    # st.image('https://images.app.goo.gl/hVVhGwZQW7iGMQ836',width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/t5FJfmOy4Ro')
    # Additional text or widgets can be added here


def ad_17():
    st.markdown("""
 17. 美国运通(American Express)，\"Do you know me?\" （你知道我吗？），
    Ogilvy & Mather ，1975

    """
    )
    # st.image('https://images.app.goo.gl/hVVhGwZQW7iGMQ836',width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/eMBS4PS-wFc')
    # Additional text or widgets can be added here



def ad_18():
    st.markdown("""
18. 美国陆军(U.S. Army)，\"Be all that you can be\"
    （成为最好的自己）， N.W. Ayer & Son ，1981

    """
    )
    # st.image('https://images.app.goo.gl/hVVhGwZQW7iGMQ836',width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/ms9pxvEbILs')
    # Additional text or widgets can be added here


def ad_19():
    st.markdown("""
    19. 安乃静解热去痛片(Anacin)，\"Fast, fast, fast relief\"
    (快、快、快速见效)， Ted Bates & Co. ，1952
    """
    )
    # st.image('https://images.app.goo.gl/hVVhGwZQW7iGMQ836',width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/Tm1Ak-B0BWs')
    # Additional text or widgets can be added here


def ad_20():
    st.markdown("""
    20. 滚石乐队(Rolling Stone)，\"Perception. Reality.\"
    （真实的感觉），FMR（Fallon McElligott Rice），1985 
    """
    )
    st.image('https://static-prod.adweek.com/wp-content/uploads/2017/09/rs-19.jpg',width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://youtu.be/Tm1Ak-B0BWs')
    # Additional text or widgets can be added here



def ad_21():
    st.markdown("""
    21. 百事可乐(Pepsi-Cola)，\"The Pepsi generation\"
    (新一代的选择)，BBDO，1964
    """
    )
    # st.image('https://static-prod.adweek.com/wp-content/uploads/2017/09/rs-19.jpg',width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/QWQkf0w5JR4')
    # Additional text or widgets can be added here



def ad_22():
    st.markdown("""
22. 哈斯维衬衫(Hathaway Shirts)，\"The man in the Hathaway shirt\"
    （穿哈斯维的男人），Hewitt, Ogilvy, Benson & Mather ，1951
    """
    )
    st.image('https://i0.wp.com/georgehahn.com/wp-content/uploads/2012/01/the-man-in-the-hathaway-shirt-ogilvy-on-illustration-in-advertising.png?resize=323%2C433&ssl=1',width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://youtu.be/QWQkf0w5JR4')
    # Additional text or widgets can be added here



def ad_23():
    st.markdown("""
23. 博马剃须刀(Burma-Shave)，" Roadside signs in verse " （路边的诗句牌
    ），Allen Odell，1925
    
    注：Burma-Shave公司在当时采用了一种独特的广告方式，他们将广告内容分成多个简短的诗句，逐个放置在沿路的标牌上，形成连贯的广告信息。这些标牌以幽默和押韵的形式传递广告信息，成为了当时非常受欢迎和具有影响力的广告形式。
    """
    )
    st.image('https://neonsignpark.com/images/2019/04/07/burmasign.jpg',width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://youtu.be/QWQkf0w5JR4')
    # Additional text or widgets can be added here


def ad_24():
    st.markdown("""
   24. 美国汉堡王(Burger King)，\"Have it your way\"
    （我选我味），BBDO，1973
    """
    )
    # st.image('https://neonsignpark.com/images/2019/04/07/burmasign.jpg',width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/KJXzkUH72cY')
    # Additional text or widgets can be added here


def ad_25():
    st.markdown("""
    25. 坎贝尔浓汤(Campbell Soup)，\"Mmm mm good\"
    （啧嘖,真好味！），BDO，20世纪30年代

    """
    )
    # st.image('https://neonsignpark.com/images/2019/04/07/burmasign.jpg',width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/KtmcW8MsCH8')
    # Additional text or widgets can be added here


def ad_26():
    st.markdown("""
  26. 美国林业总署(U.S. Forest Service)， Smokey the Bear/\"Only you can
    prevent forest fires\" （护林熊/"只有你能防止森林火灾"），Advertising
    Council/FCB
    """
    )
    # st.image('https://neonsignpark.com/images/2019/04/07/burmasign.jpg',width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/lgf9yVke8Z8')
    # Additional text or widgets can be added here


def ad_27():
    st.markdown("""
27. 百威啤酒(Budweiser)，\"This Bud\'s for you\" （为你准备的百威），
    D\'Arcy Masius Benton & Bowles ，20世纪70年代
    """
    )
    # st.image('https://neonsignpark.com/images/2019/04/07/burmasign.jpg',width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/5m7A2mEB63E')
    # Additional text or widgets can be added here


def ad_28():
    st.markdown("""
    28. 媚登峰内衣(Maidenform)，\"I dreamed I went shopping in my
    Maidenform bra\" （真想穿媚登峰内衣去逛街）， Norman, Craig &
    Kunnel，1949
    """
    )
    st.image('https://i.ebayimg.com/images/g/Su8AAOSwlNtj0Gwo/s-l1200.webp',width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://youtu.be/5m7A2mEB63E')
    # Additional text or widgets can be added here

def ad_29():
    st.markdown("""
29. 胜利唱机公司(Victor Talking Machine)，\"His master\'s voice\"
    （主人之声），Francis Barraud，1901
    """
    )
    st.image("https://upload.wikimedia.org/wikipedia/commons/2/2d/His_Master%27s_Voice.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://youtu.be/5m7A2mEB63E')
    # Additional text or widgets can be added here

def ad_30():
    st.markdown("""
    30.Jordan汽车(Jordan Motor Car Co.)，\"Somewhere west of Laramie\"
    （拉勒米以西的某处" ，Edward S. (Ned) Jordan，1923
    """
    )
    st.image("https://richardlangworth.com/wp-content/uploads/2023/03/Laramie2.jpeg",width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://youtu.be/5m7A2mEB63E')
    # Additional text or widgets can be added here


def ad_31():
    st.markdown("""
31. Woodbury香皂(Woodbury Soap)，\"The skin you love to touch\"
    （你爱触摸的肌肤），JWT，1911
    """
    )
    st.image("https://upload.wikimedia.org/wikipedia/commons/d/d7/1916-skin-touch-soap-ad.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://youtu.be/5m7A2mEB63E')
    # Additional text or widgets can be added here


def ad_32():
    st.markdown("""
32. Benson & Hedges 100s香烟，\"The disadvantages\"（有害），Wells,
    Rich, Greene，20世纪60年代
    """
    )
    # st.image("https://upload.wikimedia.org/wikipedia/commons/d/d7/1916-skin-touch-soap-ad.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/UEUHV20kH9g')
    # Additional text or widgets can be added here

def ad_33():
    st.markdown("""
33. 国民饼干(National Biscuit )，"Uneeda Biscuits\' Boy in Boots"（
    Uneeda饼干的穿靴男孩 ）， N.W. Ayer & Son ，1899
    
    注： 这是Uneeda Biscuits品牌饼干的形象广告，塑造了一个渴望 Uneeda
    Biscuits饼干的穿靴子小男孩，用以传达产品的亲和力和吸引力。
    """
    )
    st.image("https://americanbusinesshistory.org/wp-content/uploads/2021/09/apijjtjtk__76529.1626731376-706x1030.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://youtu.be/UEUHV20kH9g')
    # Additional text or widgets can be added here


def ad_34():
    st.markdown("""
    34. 劲量电池(Energizer)，"The Energizer
    Bunny"（劲量兔子），Chiat/Day，1989
    """
    )
    # st.image("https://americanbusinesshistory.org/wp-content/uploads/2021/09/apijjtjtk__76529.1626731376-706x1030.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/tH6MBpFQGyM')
    # Additional text or widgets can be added here


def ad_35():
    st.markdown("""
    35. 莫顿食盐（Morton Salt），\"When it rains it pours\"
    （下雨时，它会倾泻 ）， N.W. Ayer & Son ，1912
    
    注：这个广告语传达了Morton盐在潮湿条件下仍然能保持流动性的特点，突出了其抗结块的卖点。

    """
    )
    st.image("https://www.mortonsalt.com/wp-content/uploads/her-debut-1159x1800.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://youtu.be/tH6MBpFQGyM')
    # Additional text or widgets can be added here


def ad_36():
    st.markdown("""
36. 夏奈尔香水(Chanel)，\"Share the fantasy\" （梦幻分享），DDB，1979
    """
    )
    # st.image("https://www.mortonsalt.com/wp-content/uploads/her-debut-1159x1800.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/jBLFCQD76zk?si=KuLUikHgQWmn5lkf')
    # Additional text or widgets can be added here

def ad_37():
    st.markdown("""
   37. 通用土星汽车(Saturn)，\"A different kind of company, A different
    kind of car.\" （不一样的公司，不一样的汽车），Hal Riney & Partners
    ，1989

    """
    )
    # st.image("https://www.mortonsalt.com/wp-content/uploads/her-debut-1159x1800.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/PcJ4zNY_MUU')
    # Additional text or widgets can be added here


def ad_38():
    st.markdown("""
    38. 佳洁士牙膏(Crest toothpaste)，\"Look, Ma! No cavities!\"
    （妈妈，看，我没有蛀牙！），Benton & Bowles ，1958
    """
    )
    # st.image("https://www.mortonsalt.com/wp-content/uploads/her-debut-1159x1800.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/ocKnxSeXDwM')
    # Additional text or widgets can be added here

def ad_39():
    st.markdown("""
39. M巧克力(M&Ms)，\"Melts in your mouth, not in your hands\"
    （只溶在口，不溶在手）， Ted Bates & Co. ，1954
    """
    )
    # st.image("https://www.mortonsalt.com/wp-content/uploads/her-debut-1159x1800.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/BZUccKFxTS4')
    # Additional text or widgets can be added here


def ad_40():
    st.markdown("""
    40. 天美时手表(Timex)，\"Takes a licking and keeps on ticking\"
    （经得摔打，依旧准确 ），W.B. Doner & Co & predecessor公司，20世纪50年代
    """
    )
    # st.image("https://www.mortonsalt.com/wp-content/uploads/her-debut-1159x1800.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/hSv6Z5BA6e8')
    # Additional text or widgets can be added here


def ad_41():
    st.markdown("""
    41. 雪佛兰汽车(Chevrolet)，\"See the USA in your Chevrolet\"
    （乘雪佛兰逛美国），Campbell-Ewald，20世纪50年代
    """
    )
    # st.image("https://www.mortonsalt.com/wp-content/uploads/her-debut-1159x1800.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/nxrYO6-y4HI')
    # Additional text or widgets can be added here


def ad_42():
    st.markdown("""
    42. CK内衣(Calvin Klein)，\"Know what comes between me and my Calvins?
    Nothing!\" （我和Calvin 亲密无间）
    """
    )
    # st.image("https://www.mortonsalt.com/wp-content/uploads/her-debut-1159x1800.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/YK2VZgJ4AoM')
    # Additional text or widgets can be added here


def ad_43():
    st.markdown("""
  43. 里根竞选总统广告(Reagan for President)，\"It\'s morning again in
    America\" （美国迎来又一个清晨），Tuesday Team，1984
    """
    )
    # st.image("https://www.mortonsalt.com/wp-content/uploads/her-debut-1159x1800.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/pUMqic2IcWA')
    # Additional text or widgets can be added here



def ad_44():
    st.markdown("""
44. 云丝顿香烟(Winston cigarettes)，\"Winston tastes good--like a
    cigarette should\" （云丝顿，香烟该有的味道），1954
    """
    )
    # st.image("https://www.mortonsalt.com/wp-content/uploads/her-debut-1159x1800.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/PU3eYBM0Y30')
    # Additional text or widgets can be added here


def ad_45():
    st.markdown("""
45. 美国音乐学校(U.S. School of Music)，\"They laughed when I sat down
    at the piano, but when I started to play!\"
    （我开始演奏时，众人目瞪口呆！）， Ruthrauff & Ryan，1925
    """
    )
    st.image("https://marchingagainstphilip.wordpress.com/wp-content/uploads/2010/04/piano_ad3.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://youtu.be/PU3eYBM0Y30')
    # Additional text or widgets can be added here


def ad_46():
    st.markdown("""
    46. 骆驼香烟(Camel cigarettes)，\"I\'d walk a mile for a Camel\"
    （只为---支骆驼烟，我宁愿走一英里）， N. W. Ayer & Son ，1921
    """
    )
    st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRAu6nIR15tAA6a7VCuKgFLiU54a9jBaiuV1tRh8KpJtO4AFC6GF3lTS_YcA-Y0bRSnvnA&usqp=CAU",width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://youtu.be/PU3eYBM0Y30')
    # Additional text or widgets can be added here


def ad_47():
    st.markdown("""
47. 温迪汉堡包(Wendy\'s)，\"Where\'s the beef?\"
    （牛肉在哪里？），Dancer-Fitzgerald-Sample，1984
    """
    )
    # st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRAu6nIR15tAA6a7VCuKgFLiU54a9jBaiuV1tRh8KpJtO4AFC6GF3lTS_YcA-Y0bRSnvnA&usqp=CAU",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/cFLttH5QOFU')
    # Additional text or widgets can be added here



def ad_48():
    st.markdown("""
    48. 李斯特林漱口水（Listerine），\"Always a bridesmaid, but never a
    bride\"

    （总是伴娘，从未新娘），Lambert & Feasley，1923

    注：
    这个广告语旨在突出使用Listerine可以避免因为口臭而错失机会，暗示使用者可能从伴娘成为新娘。
    """
    )
    st.image("https://media-cldnry.s-nbcnews.com/image/upload/t_fit-760w,f_auto,q_auto:best/newscms/2016_32/1150147/mwo7i.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://youtu.be/cFLttH5QOFU')
    # Additional text or widgets can be added here


def ad_49():
    st.markdown("""
 49. 卡迪拉克(Cadillac)，\"The penalty of leadership\"\
    （出人头地的代价），MacManus, John & Adams，1915
    """
    )
    st.image("https://assets.entrepreneur.com/images/misc/1489481158_PenaltyofLeadership.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://youtu.be/cFLttH5QOFU')
    # Additional text or widgets can be added here


def ad_50():
    st.markdown("""
   50. 让美国美丽组织（Keep America Beautiful），\"Crying Indian\"
    （哭泣的印第安人），Advertising Council/Marstellar Inc.，1971
    """
    )
    # st.image("https://assets.entrepreneur.com/images/misc/1489481158_PenaltyofLeadership.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/h0sxwGlTLWw')
    # Additional text or widgets can be added here


def ad_51():
    st.markdown("""
    51. 宝洁Charmin卫生纸，\"Please don\'t squeeze the Charmin\"
    （请别冷淡了Charmin），Benton & Bowles，1964
    
    注： Charmin 即 迷人的。
    """
    )
    # st.image("https://assets.entrepreneur.com/images/misc/1489481158_PenaltyofLeadership.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/gVFCm2PlXXc')
    # Additional text or widgets can be added here


def ad_52():
    st.markdown("""
52. Wheaties麦片(Wheaties)，\"Breakfast of champions\"

    （冠军的早餐），Blackett-Sample-Hummert，20世纪30年代
    """
    )
    st.image("https://tf-cmsv2-smithsonianmag-media.s3.amazonaws.com/filer/f6/d1/f6d1c97c-bbca-40e4-b8a5-15705f86a0d1/1934_elinor_smith.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://youtu.be/gVFCm2PlXXc')
    # Additional text or widgets can be added here

def ad_53():
    st.markdown("""
53. 可口可乐(Coca-Cola)，\"It\'s the real thing\" （这是真的），
    McCann-Erickson ，1970
    """
    )
    # st.image("https://tf-cmsv2-smithsonianmag-media.s3.amazonaws.com/filer/f6/d1/f6d1c97c-bbca-40e4-b8a5-15705f86a0d1/1934_elinor_smith.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/dDSnjjdGh5M')
    # Additional text or widgets can be added here


def ad_54():
    st.markdown("""
   54. 灰狗巴士(Greyhound)，\"It\'s such a comfort to take the bus and
    leave the driving to us\" （有坐车之乐，无开车之累）， Grey Advertising
    ，1957
    """
    )
    # st.image("https://tf-cmsv2-smithsonianmag-media.s3.amazonaws.com/filer/f6/d1/f6d1c97c-bbca-40e4-b8a5-15705f86a0d1/1934_elinor_smith.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/uZrhLQWGpjY')
    # Additional text or widgets can be added here


def ad_55():
    st.markdown("""
55. 家乐氏西式爆米花（Kellogg\'s Rice Krispies），\"Snap! Crackle! and
    Pop!\" （咬一口，咔嚓脆）， Leo Burnett Co. ，20世纪40年代
    """
    )
    # st.image("https://tf-cmsv2-smithsonianmag-media.s3.amazonaws.com/filer/f6/d1/f6d1c97c-bbca-40e4-b8a5-15705f86a0d1/1934_elinor_smith.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/sEPtj-AG31I')
    # Additional text or widgets can be added here


def ad_56():
    st.markdown("""
    56. 宝丽来拍立得(Polaroid)，\"It\'s so
    simple\"（就是这么简单），DDB，1977
    """
    )
    st.image("https://i.pinimg.com/originals/54/c5/19/54c519626e34809bd547662a70871ec0.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://youtu.be/4wvRJDOrGyA?si=zyQp7JFx3H4PW1-O')
    # Additional text or widgets can be added here


def ad_57():
    st.markdown("""
57. 吉列剃须刀(Gillette)，\"Look sharp, feel sharp\"
    （看似锋利，确实锋利），BBDO，20世纪40年代
    """
    )
    # st.image("https://i.pinimg.com/originals/54/c5/19/54c519626e34809bd547662a70871ec0.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/UmxbYee6sFA')
    # Additional text or widgets can be added here


def ad_58():
    st.markdown("""
    58. 莱唯斯雷面包(Levy\'s Rye Bread)，\"You don\'t have to be Jewish to
    love Levy\'s Rye Bread\" （不是犹太人也照样喜欢莱唯斯雷面包），DDB，1949
    """
    )
    # st.image("https://i.pinimg.com/originals/54/c5/19/54c519626e34809bd547662a70871ec0.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/9gugWKeRZ4w')
    # Additional text or widgets can be added here

def ad_59():
    st.markdown("""
 59. Pepsodent增白牙膏，\"You\'ll wonder where the yellow went\"
    （奇怪，黄斑哪去了），FCB，1956
    """
    )
    # st.image("https://i.pinimg.com/originals/54/c5/19/54c519626e34809bd547662a70871ec0.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/UP2h4LjBXu0')
    # Additional text or widgets can be added here


def ad_60():
    st.markdown("""
60. Lucky Strike香烟，\"Reach for a Lucky instead of a sweet\"
    （好运胜过甜蜜），Lord & Thomas，20世纪20年代
    """
    )
    st.image("https://tobacco-img.stanford.edu/wp-content/uploads/cigarettes/keeps-you-slim/instead-of-a-sweet/sweet_1.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://youtu.be/UP2h4LjBXu0')
    # Additional text or widgets can be added here

def ad_61():
    st.markdown("""
61. 七喜汽水(7 UP)，\"The Uncola\" （并非可乐），JWT，20世纪70年代
    """
    )
    # st.image("https://tobacco-img.stanford.edu/wp-content/uploads/cigarettes/keeps-you-slim/instead-of-a-sweet/sweet_1.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/AXmc7DG4uu8')
    # Additional text or widgets can be added here

def ad_62():
    st.markdown("""
    62. 威斯克洗衣粉 (Wisk detergent)，\"Ring around the collar\"
    （洁淨领渍），BBDO，1968
    """
    )
    # st.image("https://tobacco-img.stanford.edu/wp-content/uploads/cigarettes/keeps-you-slim/instead-of-a-sweet/sweet_1.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/K5paMDrnON4')
    # Additional text or widgets can be added here


def ad_63():
    st.markdown("""
 63. 西梅精华(Sunsweet Prunes)，\"Today the pits, tomorrow the
    wrinkles\" (今时之斑点，明日出皱纹），Freberg Ltd.，20世纪70年代
    """
    )
    # st.image("https://tobacco-img.stanford.edu/wp-content/uploads/cigarettes/keeps-you-slim/instead-of-a-sweet/sweet_1.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/eRDLaSG6csA')
    # Additional text or widgets can be added here



def ad_64():
    st.markdown("""
64. Life 麦片(Life cerea)，"Hey, Mikey"（嘿，米奇），DDB，1972
    """
    )
    # st.image("https://tobacco-img.stanford.edu/wp-content/uploads/cigarettes/keeps-you-slim/instead-of-a-sweet/sweet_1.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/vYEXzx-TINc')
    # Additional text or widgets can be added here


def ad_65():
    st.markdown("""
    65. 赫兹租车公司(Hertz)，\"Let Hertz put you in the driver\'s seat\"
    （让赫兹把你带到驾驶座上 ），Norman, Craig & Kummel，1961
    """
    )
    # st.image("https://tobacco-img.stanford.edu/wp-content/uploads/cigarettes/keeps-you-slim/instead-of-a-sweet/sweet_1.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/p4qslTTVNt4')
    # Additional text or widgets can be added here


def ad_66():
    st.markdown("""
 66. Foster Grant太阳镜，\"Who\'s that behind those Foster Grants?\"
    （戴Foster Grants太阳镜的是谁？）,Geer, Dubois，1965
    """
    )
    # st.image("https://tobacco-img.stanford.edu/wp-content/uploads/cigarettes/keeps-you-slim/instead-of-a-sweet/sweet_1.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/I308QffO-SU')
    # Additional text or widgets can be added here



def ad_67():
    st.markdown("""
   67. 柏杜鸡（Perdue chicken），\"It takes a tough man to make tender
    chicken\" （硬汉也能做出鲜嫩鸡肉）， Scali, McCabe, Sloves , 1971
    """
    )
    # st.image("https://tobacco-img.stanford.edu/wp-content/uploads/cigarettes/keeps-you-slim/instead-of-a-sweet/sweet_1.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/9Z789aLNfXo')
    # Additional text or widgets can be added here



def ad_68():
    st.markdown("""
    68. 贺曼卡片(Hallmark)，\"When you care enough to send the very best\"
    （如果你真的在乎，就寄最好的贺卡），FCB，20世纪30年代
    """
    )
    st.image("https://d1f5kcwhveewqf.cloudfront.net/uploads/timeline/1944-hallmark.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://youtu.be/9Z789aLNfXo')
    # Additional text or widgets can be added here



def ad_69():
    st.markdown("""
   69. Springmaid 床单，\"A buck well spent\" （物有所值），
    In-house，1948
    """
    )
    st.image("https://i.pinimg.com/originals/15/07/f9/1507f92f809d2cad80fce8dcf0a472b8.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://youtu.be/9Z789aLNfXo')
    # Additional text or widgets can be added here


def ad_70():
    st.markdown("""
    70. Queensboro 集团，" Jackson Heights Apartment
    Homes"（杰克逊高地公寓之家），WEAF, NYC，20世纪20年代
    """
    )
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Jackson_Heights_Advertisement_by_The_Queensboro_Corporation.jpg/640px-Jackson_Heights_Advertisement_by_The_Queensboro_Corporation.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://youtu.be/9Z789aLNfXo')
    # Additional text or widgets can be added here


def ad_71():
    st.markdown("""
    71. 施坦威钢琴（Steinway & Sons）, \"The instrument of the immortals\"
    （不朽的乐器）, N.W. Ayer & Sons , 1919
    """
    )
    st.image("https://miro.medium.com/v2/resize:fit:944/1*Da1rfCL9czREXblEALdxXA.jpeg",width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://youtu.be/9Z789aLNfXo')
    # Additional text or widgets can be added here


def ad_72():
    st.markdown("""
72. Levi's牛仔裤，\"501 Blues\" （501款蓝色牛仔裤），FCB，1984
    """
    )
    # st.image("https://youtu.be/YaXFXo-1KCE",width=600)
    # st.video('https://vimeo.com/191873873')
    st_player('https://youtu.be/YaXFXo-1KCE')
    # Additional text or widgets can be added here



def ad_73():
    st.markdown("""
    73. 黑玉蝠貂 (Blackglama-Great Lakes Mink)，\"What becomes a legend
    most?\" （什么最适合传奇？） ， Jane Trahey Associates ，20世纪60年代

    注：
    这个广告语以神秘和优雅的方式强调了Blackglama水貂皮草的高贵和经典地位。
    """
    )
    st.image("https://fur.org/wp-content/uploads/2021/05/Black-Glama-1.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://youtu.be/R2vNdROz7xg')
    # Additional text or widgets can be added here


def ad_74():
    st.markdown("""
    74. 蓝仙姑葡萄酒（Blue Nun），"Stiller & Meara campaign"
    （斯蒂勒与米拉广告喜剧），Della Famina, Travisano & Partners，
    20世纪70年代

    注： 这个广告活动以喜剧演员夫妇Jerry Stiller和Anne
    Meara的幽默表演著称，用以宣传Blue Nun葡萄酒。
    """
    )
    # st.image("https://fur.org/wp-content/uploads/2021/05/Black-Glama-1.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://youtu.be/yfzXrLT8_fs')
    st.video('https://youtu.be/yfzXrLT8_fs')
    # Additional text or widgets can be added here


def ad_75():
    st.markdown("""
    75. 哈姆啤酒（Hamm\'s beer），\"From the Land of Sky Blue Waters\"
    "源自蓝天水乡"，Campbell-Mithun，20世纪50年代
    """
    )
    # st.image("https://fur.org/wp-content/uploads/2021/05/Black-Glama-1.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://www.dailymotion.com/video/xvlqk')
    st.video('https://youtu.be/7ZC3NUdjtug')
    # Additional text or widgets can be added here


def ad_76():
    st.markdown("""
    76. Quaker Puffed麦片，"Shot from guns " （枪炮爆米花 ），Lord &
    Thomas，20世纪20年代

    注： 这个广告强调了Quaker
    Puffed谷物采用高压加热的制作工艺，使其谷物膨化如同从枪炮中射出一样。
    """
    )
    # st.image("https://fur.org/wp-content/uploads/2021/05/Black-Glama-1.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://www.dailymotion.com/video/xvlqk')
    st.video('https://youtu.be/zGpS6LHeBC0')
    # Additional text or widgets can be added here

def ad_77():
    st.markdown("""
    77. ESPN体育频道，\"This is SportsCenter\" "这里是体育中心"， Wieden &
    Kennedy， 1995
    """
    )
    # st.image("https://fur.org/wp-content/uploads/2021/05/Black-Glama-1.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://www.dailymotion.com/video/xvlqk')
    st.video('https://youtu.be/2f6lNBsBb9k')
    # Additional text or widgets can be added here

def ad_78():
    st.markdown("""
    78. Molson啤酒，" Laughing Couple"（欢笑的一对），Moving & Talking
    Picture Co.，20世纪80年代
    """
    )
    # st.image("https://fur.org/wp-content/uploads/2021/05/Black-Glama-1.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://www.dailymotion.com/video/xvlqk')
    st.video('https://youtu.be/Eps72hsxTu4')
    # Additional text or widgets can be added here

def ad_79():
    st.markdown("""
    79. 加州乳品加工协会(California Milk Processor Board)，\"Got Milk?\"
    （喝牛奶了吗？），1993
    """
    )
    # st.image("https://fur.org/wp-content/uploads/2021/05/Black-Glama-1.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://www.dailymotion.com/video/xvlqk')
    st.video('https://youtu.be/mIaAvoQAZAU')
    # Additional text or widgets can be added here


def ad_80():
    st.markdown("""
        80. 美国电话电报公司(AT&T)，\"Reach out and touch someone\"
    "伸出臂膀，拥抱世界"， N.W. Ayer & Sons （艾尔父子广告），1979
    """
    )
    st.image("https://admeritus.com/wp-content/uploads/2020/01/09_2011_elec_141.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://www.dailymotion.com/video/xvlqk')
    # st.video('https://youtu.be/OapWdclVqEY')
    # Additional text or widgets can be added here


def ad_81():
    st.markdown("""
81. 百洁霜(Brylcreem)，\"A little dab\'ll do ya\" （每次只需一点点），
    Kenyon & Eckhardt ，20世纪50年代
    """
    )
    # st.image("https://admeritus.com/wp-content/uploads/2020/01/09_2011_elec_141.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://www.dailymotion.com/video/xvlqk')
    st.video('https://youtu.be/cmoDx2wJy1c')
    # Additional text or widgets can be added here


def ad_82():
    st.markdown("""
    82. 嘉灵黑啤酒(Carling Black Label beer)，\"Hey Mabel, Black Label!\"
    "嗨！梅布尔，嘉灵黑牌"， Lang, Fisher & Stashower ，20世纪40年代
    """
    )
    st.image("https://www.taverntrove.com/imagecache/carlings-black-label-beer-paper-ads-carling-brewing-company_81198-1.jpg_H828.jpg",width=600)
    # st.video('https://vimeo.com/191873873')
    # st_player('https://www.dailymotion.com/video/xvlqk')
    # st.video('https://youtu.be/cmoDx2wJy1c')
    # Additional text or widgets can be added here

def ad_83():
    st.markdown("""
   83. 五十铃 (Isuzu) ，\"Lying Joe Isuzu\" （说谎的乔•五十铃）， Della
    Famina, Travisano & Partners ，20世纪80年代
    """
    )
    # st.image("https://www.taverntrove.com/imagecache/carlings-black-label-beer-paper-ads-carling-brewing-company_81198-1.jpg_H828.jpg",width=600)
    st.video('https://youtu.be/wtX5m09YjQ4')
    # st_player('https://www.dailymotion.com/video/xvlqk')

def ad_84():
    st.markdown("""
    84. 宝马(BMW)，\"The ultimate driving machine\" "终极驾驶机器"，
    Ammirati & Puris ，1975年
    """
    )
    # st.image("https://www.taverntrove.com/imagecache/carlings-black-label-beer-paper-ads-carling-brewing-company_81198-1.jpg_H828.jpg",width=600)
    st.video('https://youtu.be/qW9C5ggIJEg')
    # st_player('https://www.dailymotion.com/video/xvlqk')


def ad_85():
    st.markdown("""
    85. 德士古公司(Texaco)， \"You can trust your car to the men who wear
    the star\"  "你的车可托付给佩戴星标的人"， Benton & Bowles ，20世纪40年代
    """
    )
    # st.image("https://www.taverntrove.com/imagecache/carlings-black-label-beer-paper-ads-carling-brewing-company_81198-1.jpg_H828.jpg",width=600)
    st.video('https://youtu.be/b1zxOTDHIBQ')
    # st_player('https://www.dailymotion.com/video/xvlqk')


def ad_86():
    st.markdown("""
 86. 可口可乐 (Coca-Cola )，\"Always\" "永远的可口可乐"， Creative
    Artists Agency ，1993年
    """
    )
    # st.image("https://www.taverntrove.com/imagecache/carlings-black-label-beer-paper-ads-carling-brewing-company_81198-1.jpg_H828.jpg",width=600)
    st.video('https://youtu.be/kCVTNKXOYqk')
    # st_player('https://www.dailymotion.com/video/xvlqk')



def ad_87():
    st.markdown("""
  87. 施乐(Xerox)，\"It\'s a miracle\" （它是个奇迹）， Needham, Harper &
    Steers ，1975年

    """
    )
    # st.image("https://www.taverntrove.com/imagecache/carlings-black-label-beer-paper-ads-carling-brewing-company_81198-1.jpg_H828.jpg",width=600)
    st.video('https://youtu.be/LAt-lB9JIqw')
    # st_player('https://www.dailymotion.com/video/xvlqk')

def ad_88():
    st.markdown("""
    88. 巴特尔•杰默斯葡萄酒(Bartles & Jaymes)，\"Frank and Ed\"
    （弗兰克和埃德）， Hal Riney & Partners ，1985年

    """
    )
    # st.image("https://www.taverntrove.com/imagecache/carlings-black-label-beer-paper-ads-carling-brewing-company_81198-1.jpg_H828.jpg",width=600)
    st.video('https://youtu.be/dRYbF296964')
    # st_player('https://www.dailymotion.com/video/xvlqk')


def ad_89():
    st.markdown("""
    89. 达能酸奶(Dannon Yogurt)，\"Old People in Russia\" "俄罗斯的老人"，
    Marstellar Inc. ，20世纪70年代
    """
    )
    # st.image("https://www.taverntrove.com/imagecache/carlings-black-label-beer-paper-ads-carling-brewing-company_81198-1.jpg_H828.jpg",width=600)
    st.video('https://youtu.be/GXzVDvWMIuI')
    # st_player('https://www.dailymotion.com/video/xvlqk')



def ad_90():
    st.markdown("""
    90. 沃尔沃(Volvo)，" Average life of a car in
    Sweden""车在瑞典的平均寿命"， Scali, McCabe, Sloves ，20世纪60年
    """
    )
    st.image("https://i.pinimg.com/736x/dd/9b/0a/dd9b0a8a7e53551877c7feff1813ee78.jpg",width=600)
    # st.video('https://youtu.be/GXzVDvWMIuI')
    # st_player('https://www.dailymotion.com/video/xvlqk')



def ad_91():
    st.markdown("""
 91. 6号汽车旅馆(Motel 6)，\"We\'ll leave a light on for you\"
    "始终为你亮灯"， Richards Group ，1988年
    """
    )
    st.image("https://media.licdn.com/dms/image/D5616AQH0q-slkFRfnQ/profile-displaybackgroundimage-shrink_200_800/0/1721934229172?e=2147483647&v=beta&t=CJzXCtiyOcMeQre6p4YczBI5KDes8vUGmgs5dl_AVxw",width=600)
    # st.video('https://youtu.be/GXzVDvWMIuI')
    # st_player('https://www.dailymotion.com/video/xvlqk')


def ad_92():
    st.markdown("""
    92.果冻(Jell-O)，"Bill Cosby with kids"（比尔•考斯比和孩子们）， Young &
    Rubicam ，1975年
    """
    )
    # st.image("https://media.licdn.com/dms/image/D5616AQH0q-slkFRfnQ/profile-displaybackgroundimage-shrink_200_800/0/1721934229172?e=2147483647&v=beta&t=CJzXCtiyOcMeQre6p4YczBI5KDes8vUGmgs5dl_AVxw",width=600)
    st.video('https://youtu.be/EmumqhYbRE0')
    # st_player('https://www.dailymotion.com/video/xvlqk')


def ad_93():
    st.markdown("""
    93. IBM，"Chaplin\'s Little Tramp character""小丑卓别林"， Lord,
    Geller, Federico, EinsteinLord, Geller, Federico, Einstein ，1982年
    """
    )
    # st.image("https://media.licdn.com/dms/image/D5616AQH0q-slkFRfnQ/profile-displaybackgroundimage-shrink_200_800/0/1721934229172?e=2147483647&v=beta&t=CJzXCtiyOcMeQre6p4YczBI5KDes8vUGmgs5dl_AVxw",width=600)
    st.video('https://youtu.be/1LR1Xvvch18')
    # st_player('https://www.dailymotion.com/video/xvlqk')

def ad_94():
    st.markdown("""
    94. 美国旅行者箱包(American Tourister)，"The
    Gorilla"（大猩猩），DDB，20世纪60年代晚期
    """
    )
    # st.image("https://media.licdn.com/dms/image/D5616AQH0q-slkFRfnQ/profile-displaybackgroundimage-shrink_200_800/0/1721934229172?e=2147483647&v=beta&t=CJzXCtiyOcMeQre6p4YczBI5KDes8vUGmgs5dl_AVxw",width=600)
    st.video('https://youtu.be/Q5sEIWlQO7A')
    # st_player('https://www.dailymotion.com/video/xvlqk')


def ad_95():
    st.markdown("""
    95. 赞宝除臭剂(Right Guard)，\"Medecine Cabinet\"
    （药柜），BBDO，20世纪60年代
    """
    )
    # st.image("https://media.licdn.com/dms/image/D5616AQH0q-slkFRfnQ/profile-displaybackgroundimage-shrink_200_800/0/1721934229172?e=2147483647&v=beta&t=CJzXCtiyOcMeQre6p4YczBI5KDes8vUGmgs5dl_AVxw",width=600)
    st.video('https://youtu.be/NFzC-zvDoPE?si=bLFjlLlzP2mqWvPi')
    # st_player('https://www.dailymotion.com/video/xvlqk')


def ad_96():
    st.markdown("""
    96. 梅宝(Maypo)，\"I want my Maypo\" （我要我的梅宝）， Fletcher,
    Calkins & Holden ，20世纪60年代
    """
    )
    # st.image("https://media.licdn.com/dms/image/D5616AQH0q-slkFRfnQ/profile-displaybackgroundimage-shrink_200_800/0/1721934229172?e=2147483647&v=beta&t=CJzXCtiyOcMeQre6p4YczBI5KDes8vUGmgs5dl_AVxw",width=600)
    st.video('https://youtu.be/RZygpm7p6TE')
    # st_player('https://www.dailymotion.com/video/xvlqk')


def ad_97():
    st.markdown("""
    97. 百服宁(Bufferin)，" Pounding heartbeat"（強有力的心跳）， Young &
    Rubicam ，1960年
    """
    )
    # st.image("https://media.licdn.com/dms/image/D5616AQH0q-slkFRfnQ/profile-displaybackgroundimage-shrink_200_800/0/1721934229172?e=2147483647&v=beta&t=CJzXCtiyOcMeQre6p4YczBI5KDes8vUGmgs5dl_AVxw",width=600)
    st.video('https://youtu.be/YXwWum4rkEU')
    # st_player('https://www.dailymotion.com/video/xvlqk')



def ad_98():
    st.markdown("""
    98. 箭牌衬衫(Arrow Shirts)，\"My friend, Joe Holmes, is now a horse\"
    （我的朋友乔•霍尔姆斯，（穿箭牌）如同马）， Young & Rubicam ，1938年
    """
    )
    st.image("https://www.copernicanshift.com/wp-content/uploads/2017/05/My-Best-Friend-Joe-Holmes-is-Now-a-Horse.jpg",width=600)
    # st_player('https://www.dailymotion.com/video/xvlqk')


def ad_99():
    st.markdown("""
    99. 扬•罗必凯自身广告(Young & Rubicam)，\"Impact\" （震撼）， Young &
    Rubicam ，1930年
    """
    )
    st.image("https://i0.wp.com/img.photobucket.com/albums/v259/paularubia/Vintage%20Ads/young_and_rubicam_advertising_1936.jpg",width=600)
    # st_player('https://www.dailymotion.com/video/xvlqk')


def ad_100():
    st.markdown("""
  100. 林登•约翰逊竞选美国总统(Lyndon Johnson for Presiden)，\"Daisy\"
    （雏菊），DDB，1964年
    """
    )
    st.video('https://youtu.be/-ynEiRvxazU')
    # st_player('https://www.dailymotion.com/video/xvlqk')


def classic_ad():
    st.write("# 附录3： 20世纪最成功的广告T0P100 👋")

    st.markdown("""

1999年《广告时代》（AA)杂志评选出20世纪最成功的百強广告活动，入选广告需达到或通过以下三条标准之一：

    A、是否构成了广告或社会流行文化的分水岭；
    B、是否促进了新品类的形成或帮助客户品牌成为其所属行业的龙头；
    C、是否令人难以忘怀。


**榜单排名如下（品牌名称-广告语-广告代理商及时间）：**
 """)

    # ad_1()
    # ad_2()
    # ad_3()
    # ad_4()
    # ad_5()
    # ad_6()

    for i in range(1, 101):
        func_name = "ad_" + str(i)
        try:
            globals()[func_name]()
        except:
            print("game over")

    st.markdown("""

    以上入选的广告20世纪百佳广告，每一个都有其精彩的故事。单光凭一句简单的广告语，不知其背景和场景，实难以理解这些广告何以伟大广告的奧秘。让我们以最后一条入选广告为例略作说明：

    林登·约翰逊（Lyndon B.
    Johnson）是美国历史上的一位总统，他在1963年至1969年间任职。1964年他竞选总统期间，出现了一则非常有名称为\"Daisy\"的广告。

    这则广告最初于1964年9月7日播放，是约翰逊竞选团队制作的。广告的主要内容是一个可爱的小女孩在一个花园里，她正在数着雏菊的花瓣。当她数到"9"时，画面切换到一个导弹发射的场景，接着是一个巨大的爆炸蘑菇云。广告结束时，有一个声音在背景说：\"这次选举，请投票给约翰逊。因为你的生活和你的孩子的生活取决于它，每一天都可能下（蘑菇）雨。\"

    \"Daisy\"广告的目的是通过暗示共和党候选人巴里·戈德沃特（Barry
    Goldwater）对核武器使用的立场，表达对他激进的军事政策的担忧。这则广告的情感强烈，利用了对核战争的普遍恐惧，试图让选民相信如果选错了总统，可能会导致灾难性的后果。

    这则广告引起了很大的争议，一些人批评它是在利用恐惧来获得选民的支持，而其他人则认为它成功地传达了对戈德沃特的担忧。不管怎样，这则\"Daisy\"广告在美国政治广告的历史上留下了深远的影响，被认为是一种将情感与政治联系起来的典型例子。

    来源：该榜单英文源于广告时代（AA），

    Ad Age Advertising Century: Top 100 Campaigns[EB/OL]//Ad Age.
    (1999-03-29)[2023-12-21].
    https://adage.com/article/special-report-the-advertising-century/ad-age-advertising-century-top-100-advertising-campaigns/140150.
     """)
