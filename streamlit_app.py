import json

import dotenv
import markdown
import openai
import pandas as pd
import streamlit as st
from PIL import Image

# Load environment variables
ENV = dotenv.dotenv_values(".env")

openai.api_type = "azure"
openai.api_base = ENV["AZURE_OPENAI_ENDPOINT"]
openai.api_version = ENV["AZURE_OPENAI_API_VERSION"]
openai.api_key = ENV["AZURE_OPENAI_KEY"]
# endregion


def generate_response(prompt):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    try:
        completion = openai.ChatCompletion.create(
            engine=ENV["AZURE_OPENAI_CHATGPT_DEPLOYMENT"],
            messages=st.session_state["messages"],
        )
        response = completion.choices[0].message.content
    except openai.error.APIError as e:
        st.write(response)
        response = f"The API could not handle this content: {str(e)}"
    st.session_state["messages"].append({"role": "assistant", "content": response})

    # print(st.session_state['messages'])
    total_tokens = completion.usage.total_tokens
    prompt_tokens = completion.usage.prompt_tokens
    completion_tokens = completion.usage.completion_tokens
    return response, total_tokens, prompt_tokens, completion_tokens

def intro():
    import streamlit as st

    st.write("# 欢迎来到广告思想简史! 👋")
    st.sidebar.success("栏目内容.")

    img = Image.open('statics/cover.jpeg')
    st.image(img)

    st.markdown(
        """
        本书是广告思想史的开源之作，将广告史从“WHAT”(是什么）为主的记事模式转向“WHY+HOW”(为何和如何）为主的探究模式；从关注事件转向以人物和思想为核心；从只讲“过去”延伸至“现在及未来”，尤其剖析洞察了21世纪成为主流的数字广告。 
         

        👈 以广告内在逻辑为主、辅以外部的视角，全书12章系统揭示了近120年广告波澜闳阔、柳暗花明的发展脉络和思想变迁，包括人物流派、重大主题、经典个案、数据印证和里程碑。本书凸现关键的核心思想及多元视角，并激发思考，是简明把握广告思想演变精髓及其历史走势的必读首选，适合所有对广告有兴趣的人群，尤其经济管理和传播广告类的本科生和研究生，宜作为相关专业的教材或主要参考书。 

        ### 简目


        **序**
        
        1.  **广告基因**：神奇三角商业模式 
        
            <span style="color: orange;">**里程碑1：广告商业模式**</span>
        
        2.  **拓荒转型**：迈向现代广告
            
             <span style="color: orange;">**里程碑2：韦兰德·艾尔和广告代理公司的转型**</span>
        
        3.  **立基先驱**：现代广告的早期丰碑 
        
             <span style="color: orange;">**里程碑3：专业广告文案之确立**</span>
        
        
        4.  **科学广告**：从混沌走向专业 
        
             <span style="color: orange;">**里程碑4：独特销售卖点USP**</span>
             
        5.  **创意革命（上）**：背景和三大旗手 
        
             <span style="color: orange;">**里程碑5：麦迪逊大道**</span>
             
        6.  **创意革命（下）**：创意流派与历史功勋
        
             <span style="color: orange;">**里程碑6：创意哲学与理论创新**</span>
             
        7.  **黄金时代**：广告产业的狂飇 
        
             <span style="color: orange;">**里程碑7：超级碗广告**</span>
             
        8.  **广告江湖**：智力比拼和广告帝国 
        
             <span style="color: orange;">**里程碑8：20世纪广告帝国**</span>
             
        9.  **数字颠覆**：数字广告如何崛起
        
             <span style="color: orange;">**里程碑9：数字广告联盟AdSense**</span>
             
             <span style="color: orange;">**里程碑10：数字广告购买的智能化**</span>
             
             <span style="color: orange;">**里程碑11：广告计费的革命**</span>
             
        
        10. **全新范式**：数字广告方法论
        
        11. **学源流长**：知识如何驱动广告
        
        12. **亦善亦恶**：广告的反思与未来 
        
             <span style="color: orange;">**里程碑12. 广告监控与法律**/span>
             
        **附录**
        
        1. 广告大事年表
        
        ２．20世纪广告百位巨星榜
        
        ３．20世纪最成功的广告Top100
        
        ４．全球最大广告主Top10
        
        **索引**
        
        **后记**
        
        
        
        ### 推荐语：
        
        对关注广告、思考历史、探究未来的读者来说，这是一本必读之著。广告是工业社会的重要现象，对人类社会的发展产生了不可替代的推动作用。这本书拨开历史变化的枝枝叶叶，梳理出广告发展背后的思想源流，拓展了广告的学术领域，并启迪我们一起思考面对数字化的挑战，广告业的发展如何从历史走向未来。
        
        **陈 刚 （
        北京大学教授、北京大学新闻与传播学院院长、北京大学新媒体营销传播研究中心主任）**
        
        广告的书很多，原创的不多。卢泰宏先生的这部思想史，是本难得的原创的好书。所谓思想史，就是灵魂史。不了解一个行业的思想史，难免失魂落魄。
        
        **丁俊杰（
        中国传媒大学教授、国家广告研究院院长、《国际品牌观察》杂志社社长）**
        
        卢教授的《广告创意100》曾经惊艳了一个时代，影响了我在内的一代广告人。大师新作《广告思想简史》，高屋建瓴，打开了通往未来广告之门。
        
        **林升栋
        （厦门大学、中国人民大学教授、博士生导师，厦门大学新闻与传播学院院长）**
        
        作为菲利浦•科特勒国际营销理论贡献奖中国首位获奖者，卢泰宏先生为现代营销科学在中国的传播与发展起到了重要的铺路作用。他的这部《广告思想简史》，不仅对广告的发展变迁做了"致广大而尽精微"的梳理，而且融合了基于新时代坐标的很多洞见，开卷有益，长久有益。
        
        **秦 朔（著名财经评论家，秦朔朋友圈和中国商业文明研究中心创始人）**
        
        历史背后的灵魂是思想的变迁，这本《广告思想史》以历史与逻辑相统一的视角，展开广告理论和实践120年波澜壮阔、大江大海的画卷以及背后的思想本质。大家笔法，值得深读。
        
        **王 赛（杰出管理咨询顾问、科特勒咨询集团合伙人、《增长五线》作者）**
        
        在一个泛营销、泛广告时代，这本书值得每一位关心广告和品牌（自我品牌、组织品牌）的人士阅读。卢泰宏先生是广告理论在中国的启蒙传播开拓者，本书再次体现了他宏大的视野，见微知著的洞察力和永不衰竭的创新精神。
        
        **熊晓杰（中国文旅实战战略家、时代文旅董事长）**


        ### 作者简介
    """
        , unsafe_allow_html=True)

    img = Image.open('statics/author.jpeg')
    st.image(img, width=300)

    st.markdown(
        """
        - 卢泰宏是中国中山大学二级教授、中国营销研究中心(CMC)创始人。菲利浦.科特勒(Philip Kotler)国际营销理论贡献奖( Kotler Marketing Award-Theory )大中华区首位获奖者，荣获国家教委首届人文社科优秀著作一等奖。他培养了市场营销学博士硕士百余人。兼任过国内外一批著名公司的咨询顾问。被评为“中国广告20年20人” (2001)、“影响中国营销进程的25位风云人物”(2004)、“中国最具影响力的10位管理学教授”（2005）和 “推动中国品牌化进程的50位风云人物”（2007) 等。主要论著有: MARKETING MANAGEMENT IN CHINA (with P.Kotler and K.L.Keller), 《品牌思想简史》和《消费者行为学—透视中国消费者》等
    """
        , unsafe_allow_html=True)


def memorabilia():
    import streamlit as st

    st.write("# 附录1 ：广告大事年表 👋")

    st.markdown(
        """

**15-18世纪**

-   1450年 约翰内斯·古腾堡发明了**活字印刷术。**

-   960-1127年（北宋）
    中国济南"刘家功夫针铺"的广告铜板。（"济南刘家功夫针铺""认门前白兔儿为记
    "）

-   1472年 世界上第一份**印刷广告**
    1472年德国印刷工匠克雷门茨·门德尔斯发行了一份宣传圣诞节的印刷广告。从此广告可能大规模传播。

-   1704年 **第一份报纸广告** 1704年波士顿的《波士顿新闻信使》（. the
    Boston
    News-Letter）发布了美国历史上的第一则报纸广告（促销一项物品）。

-   **1796 年　平版印刷**工艺得到完善，插图海报出现。

-   1786-1812年 英国出现早期广告公司。

**19世纪**

-   1840年 帕尔默(V.B. Palmer)在美国成立第一间广告代理公司。

-   1865年 英国的现代广告之父巴雷特(Thomas J. Barratt)为梨皂（Pears
    Soap）开创品牌广告。

-   1869 年 在美国费城创立的艾耶（父子）广告公司（N.W. Ayer & Son,
    **Inc.**）实现了广告代理的现代转型：从为媒体服务转向为广告主（企业）服务。

-   1877年 JWT 广告公司创立。

-   1880年
    瓦纳马克（J.Wanamaker）开创为百货商店雇佣全职广告文案员（John E.
    Powers）之先例。

-   1881年 Lord & Thomas 广告公司创立（芝加哥）。

-   1882年 P&G公司首次投放广告（Ivory soap，年预算$11000）

-   1886年 Coca Cola 的Logo和广告。

-   1888年左右 最早的广告业杂志：罗威尔（George P.
    Rowell）在波士顿创办名为*Printers\'s
    Ink*（《印刷者的墨迹》）的杂志。

-   1892年 艾耶广告公司首次设立专职广告文案人员岗位。（）

-   1892年
    西尔斯（Sears）发起大规模的直邮广告。以8，000张明信片获得了2，000个新订单。

-   1899年 JWT 首次在海外（英国）设立分公司。

**1900-1920年代**

-   1905年 美国广告协会（American Advertising Federation, AAF）成立。

-   1911年 JWT为Woodbury Soap的广告首次引入性感元素（\"The skin you love to touch\"）。

-   1917年 美国广告代理商协会（4A）成立，创始会员111名。

-   1917年 广告业专业协会（Institute of Practitioners in Advertising,  IPA）成立（英国）

-   1900年 第一个广告学研究机构在美国西北大学（Northwestern  University）成立。

-   1903年 斯科特（W.D.Scott）出版 The Theory of Advertising （《广告理论》）

-   1915年  霍奇基斯（G.B.Hotchkiss）在纽约大学建立了第一个广告学和营销学系。

-   1925年 克莱普纳（O Kleppner）出版 *Advertising  Procedure（《广告学教程》）

-   1922年 第一次广播广告。美国的WEAF广播电台播放的AT&T广告是广播广告的开始。

-   1923年 Young & Rubicam 公司创立。

-   1925年 英国 BURBERRYS的品牌广告。

-   1929年 美国烟草公司为Lucky Strikes 投入广告费1230万美元，创下单一产品最高广告费纪录。

-   1923年 霍普金斯（Claude C. Hopkins）出版著作《科学的广告》（Scientific Advertising）。

**1930-1940年代**

-   1930年 广告时代 "Advertising Age"（AA）创刊。

-   1932 年 卡普莱斯（John Caples）出版《广告测试方法》（Tested Advertising Methods ）。

-   1935年 李奥贝纳公司（Leo Burnett）创立。

-   1936年 "生活"（Life）杂志创刊，后成为第一本年广告费达1亿美元的杂志。

-   1938年 国际广告协会IAA 成立。

-   1941年 美国NBC电视台播放**第一个电视广告**（Bulova手表），电视广告很快席卷全球。

-   1947年 居全球首位的JWT广告公司年营业额突破100亿美元。

-   1949年 DDB 公司创立。

-   1940年代 雷斯（R .Reeves）提出影响久远的USP理论。

**1950年代**

-   1953年 设立广告研究基金（The Advertising Research Foundation is established）。

-   1954年 CBS 成为世界上最大的广告媒体。

-   1954年 电影广告媒体代理商发起戛纳国际电影广告节 （ Cannes Advertising Festival）。戛纳广告奖有\"广告界奥斯卡\"美誉。（2011年，"戛纳国际广告节"更名为"戛纳国际创意节(Cannes Lions)"。

-   1955年 品牌形象论及经典的万宝路广告 The Marlboro Man（李奥贝纳）问世。

-   1957年 帕卡德（Vance Packard）的书\"The Hidden Persuaders\" （《隐蔽的劝说者》）出版并畅销。

-   1959年 BBD（恒美）广告公司为大众车"Think small"（从小处着想）的新广告，打响了创意大革命的第一枪。伯恩巴赫开创"创意团队"的新方式：将广告文案和艺术指导整合在同一作业团队中。

**1960年代**

-   1962年 奥格威的《一个广告人的自白》（Confessions of an Advertising Man）出版，产生极大的影响。

-   1960年代 DDB广告公司提出ROI（相关性/原创性/震撼性）创意原则。

-   1964年 奥美广告公司（O&M）创立。（1948年成立O&M的前身公司）。

-   1967年 美国超级碗广告问世，后成为影响最大最昂贵的电视广告标杆。

-   1960年代 广告业开始使用计算机技术分析广告投放和数据、测量广告效果。是数据驱动广告的先声。

**1970年代**

-   1971年 美国国会禁止烟草的广播广告。

-   1972年 里斯（Al Ries）和特劳特（Jack Trout）提出广告定位论（Positioning）。

-   1975年 宝马汽车的定位广告"驾驶者的乐趣"。

**1980年代**

-   1980年 Ted Turner 创立 CNN.

-   1981年 MTV亮相，狂热的视频对广告产生大的冲击。

-   1983年 互联网问世，使在线数字广告成为可能。

-   1983年 百事可乐推出 "新一代" 广告系列（天联广告），以崛起的超级巨星迈克尔杰克逊为特色，耗资550万美元。音乐、体育和明星在电视广告中变得司空见惯。

-   1984年 苹果公司的电视广告"1984"， 产生革命性的深远影响。

-   1985年，美国广告支出超过1000亿美元，广告主单一公司（例如通用汽车和宝洁）每年广告花费超过10亿美元。

-   1986年Needham Harper，DDB和BBDO三大广告公司的合并成当时世界上最大的广告集团公司宏盟（Omnicom）。被"时代"杂志称为"大爆炸"（the big bang）。

-   1986年 Saatchi & Saatchi 收购达彼思全球（Ted Bates Worldwide），因而成为最大的广告控股公司。

-   1987年 全球广告公司的鼻祖智威汤逊集团（JWT Group）被索雷尔（Martin Sorrell）的WPP強力吞购，是资本改变全球广告业格局的最典型事件。

-   1988年 WPP 以最高单价（8.64亿美元）收购奥美集团（Ogilvy Group）。

**1990年代**

-   1993年 Y&R 广告公司提出著名的品牌资产评估模型（Brand Asset Valuator）。

-   1994年 **第一个互联网广告。** 1994年HotWired.com上刊登的首个互联网展示广告（AT&T的横幅广告）开创了在线广告的先河。

-   1997年 谷歌（Google）公司创立。

-   1998年 美国年度广告支出突破2000亿美元；超级碗电视转播中30秒广告售价达130万美元。

-   1999年 "广告时代"（AA）发布"20世纪广告系列排行榜"。

-   1999年 互联网广告突破20亿美元，进军30亿美元。

**2000年代**

-   2000年  美国广告代理商的全球年营收近3000亿美元（2952.8亿美元），其中美国国内约占一半（1506.4亿美元）。

-   2001年 FCB公司被IPG收购。

-   2000年 **谷歌发明AdWords搜索引擎广告模式。**2001年谷歌公司扭亏为盈。

-   2004年Facebook创立，加上后来的Twitter等社交媒体，为社交广告、个性化广告开辟了新的广阔舞台。

-   2006年 YouTube 创立，视频广告开始发端。

-   2007年 智能手机iPhone问世。

**2010年代**

-   2010年代 广告的**数字新触点**改变了传播方式，**程序化广告购买和实时竞价广告**的创新，改变了广告购买和投放的方式，。广告效果出现突破。

-   2012年 Facebook首次公开募股。社交媒体广告迅速崛起。

-   2012年，Facebook首次推出移动广告。

-   2013年 哈佛商业评论(中文版)封面文章"传统广告已死"。

-   2015年 美国数字广告交易平台RightMedia创立，被视为**广告程序化（Programmatic Advertising）**的发端。开启广告算法的新时代。

-   2018年 广告史上最神圣的智威汤逊广告公司（JWT）被合并终结。

-   2018年 欧洲通用数据保护条例GDPR（General Data Protection Regulation）实施，对广告业的数据收集和隐私保护提出了更为严苛的強制要求。

**2020年代**

-   2020年 **移动视频广告**开始普及。

-   2020年 元宇宙开启**虚拟广告**新领域，利用增强现实（AR）和虚拟现实（VR）广告创建更沉浸式的广告体验成为趋势。

-   2022年 ChatGPT 问世。AI的影响和应用突飞猛进、日新月异。

    """
        , unsafe_allow_html=True)


def superstar():
    import streamlit as st

    st.write("# 附录2 ：20世纪广告百位巨星榜 👋")

    st.markdown(
        """

全球著名的专业期刊广告时代（AA）在1999年年末发布了"20世纪广告百位巨星榜"（TOP
100 PEOPLE OF THE
CENTURY），以下为入选者104人（有以下4席双人分享：8，14，22，48）的名单，笔者综合了其主要贡献并简洁表述之。

**1：威廉·伯恩巴赫 William Bernbach (1911-1982）**

广告创意革命的灵魂，世纪广告人物，开创了新的广告文化。

**2：小马里恩·哈珀 Marion Harper Jr.（1916-1989）**
创新开拓广告帝国的先行者

**3：李奥贝纳 Leo Burnett（1892-1971）**
品牌形象和广告"芝加哥学派"的奠基人

4：大卫·奥格威 David Ogilvy（1911-1999）全球最具魅力的广告教皇

5：罗瑟·雷斯 Rosser Reeves（1910-1984）创立了影响深远的USP理论工具

6：约翰·沃纳梅克 John
Wanamaker（1838-1922）零售广告的先驱，说出了洞察广告效果的经典名言。

7：威廉·佩利 William
Paley（1901-1990）哥伦比亚广播公司（CBS）的缔造者，广播广告的先驱

8．莫里斯·萨奇 Maurice Saatchi（1946-）和查尔斯·萨奇 Charles
Saatchi（1943-）：英国广告业的表率，资本并购广告公司的始作俑者。

9．阿尔伯特·拉斯克 Albert Lasker（1880-1952）：现代广告之父

10．杰·恰特 Jay
Chiat（1931-2002）：创造了最具震撼的电视广告"苹果电脑1984"

11. F．韦兰·艾耶 F. Wayland Ayer
（1848-1923）：现代广告公司的开创奠基者

12．赫尔特·克朗 Helmut
Krone（1925-1997）：创意革命旗帜的DDB广告公司的艺术指导

13．尼尔·麦克尔罗伊 Neil McElroy（1904-1972）：发明了品牌经理制度

14．斯坦利·雷索Stanley Resor （1879-1964）和海伦·兰斯当·雷索 Helen
Lansdowne
Resor（1886-1964）：使智威汤逊（JWT）广告公司成为全球广告人的祖庭

15．布鲁斯·巴顿 Bruce
Barton（1886-1967）：BBDO广告公司缔造者，赋广告以宗教魅力。

16．马丁·索雷尔 Martin Sorrell（1945-
）：WPP的缔造者，以并购改变了广告界。

17．亨利·卢斯 Henry
Luce（1898-1967）：他创办的《时代周刊》（time）及出版王国长远影响了世界。

18．李·克劳 Lee Clow（1942- ）：全球广告创意人的偶像。

19．玛丽·威尔斯·劳伦丝 Mary Wells Lawrence（1928- ）：广告界的无冕女王

20．阿尔弗雷德·斯隆 Alfred
Sloan（1875-1966）：将广告纳入通用汽车公司战略的企业家。

21．约翰·卡普莱斯John
Caples（1900-1990）：他的广告测试方法开创了数据驱动广告的道路。

22．丹·维登Dan Wieden（1945-2022）和戴维·肯尼迪David
Kennedy（1940-2021）：以" Just do it"成就了耐克品牌新形象。

23．霍华德·勒克·戈萨奇Howard Luck Gossage
（1917-1969）：对广告深度反思的最机巧的广告人。

24．雪莉·宝丽柯弗Shirley
Polykoff（1908-1998）：以染发的创意广告开辟出染发大市场。

25．乔伊斯·霍尔Joyce
Hall（1891-1982）：以设计创意广告开创了贺曼贺卡（hallmark）公司。

26．雷·克罗克Ray Kroc（1902-1984）：麦当劳之父，以广告建立麦当劳品牌。

27．艾伦·罗森希恩Allen Rosenshine（1939-
）：全球超级传播集团奥姆尼康创立者之一

28．克劳德·霍普金斯Claude C.
Hopkins（1866-1932）：科学广告学派的奠基人。

29．泰德·特纳Ted Turner（1938- ）：传媒巨头CNN创始人。

30．哈尔·里尼Hal Riney（1932- 2008）：软广告和感性诉求的先驱。

31．菲尔·杜森伯里Phil
Dusenberry（1936-2007）：BBDO广告公司的创意灵魂人物。

32．艾拉·赫伯特 Ira C.\"Ike\" Herbert（1927-1995）：可口可乐品牌管家

33．鲍勃·盖奇Bob Gage（1921-2000
）：提出"艺指+文案"工作模式，DDB首位艺术总监

34．康泰·纳仕 Conde Nast（1873-1942）：创办吸引高端广告商的时尚杂志

35．约翰·斯梅尔John Smale（1927-2011 ）：再造宝洁公司品牌

36．布鲁斯·克劳福德 Bruce Crawford（1929- ）：为音乐疯狂的广告人

37．约翰·肯尼迪 John E. Kennedy
（1864-1928）：广告文案的先驱，以"广告是纸上推销术"影响了拉斯克。

38．约翰·沃森John B. Watson（1878-1958）：将行为心理学注入广告的科学家。

39．史蒂夫·乔布斯（Steve Jobs ，1955-2011
）：苹果公司之父，以广告建立与众不同的品牌形象。

40．菲利斯·K．罗宾逊Phyllis K. Robinson（1921-2010 ）："我世代"倡导者

41．威廉·伦道夫·赫斯特 William Randolph
Hearst（1863-1951）：美国报业大亨。

42．菲利普·盖尔Philip Geier（1935-2019 ）：将IPG成为超大广告集团。

43．简·特雷希Jane
Trahey（1923-2000）：第一位年收入100万美元、创意出众的广告女性。广告界的女性主义者

44．约翰·约翰逊John H.
Johnson（1918-2005）：为美国媒体的彩虹增添了永久的一抹黑色。

45．乔治·盖洛普George
Gallup（1901-1984）：消费态度研究的先行者。美国民意调查创始人。

46．雷蒙德·罗必凯 Raymond
Rubicam（1892-1978）：创立Y&R广告公司，现代广告的奠基者之一。

47．基思·莱因哈德 Keith Reinhard （1935- ）：确立麦当劳的品牌个性，
Omnicom 集团创建人之一。

48．卡尔·艾利 Carl Ally（1924-1999）和阿米尔·加尔加诺 Amil
Gargano（1933-）：竞争性广告创意的成功者。

49．夏洛特·比尔斯Charlotte Beers（1935-
）：职位最高的广告女性，麦迪逊大道女王

50．大卫·萨诺夫David Sarnoff（1891-1971）：现代电视之父

51．乔治·巴顿George Batten（1854-1918）：
BBDO创建人之一，笃信宗教的广告人。

52. 詹姆斯·韦伯·杨 James Webb Young（1886-1973）：广告创意思想家。

53．杰克·廷克Jack Tinker（1906-1985）：麦肯广告公司的创意台柱。

54．李·艾可卡Lee Iacocca（1924-2019 ）：美国汽车行业的传奇广告英雄。

55．唐·贝尔丁Don Belding（1897-1969）：美国西海岸广告之父

56．西奥多·麦克马纳斯Theodore F.
MacManus（1872-1940）：品牌价值观广告的开创者。

57．西尔维斯特·帕特·韦弗 Sylvester L.\"Pat\" Weaver（1908-2002
）：广播电视广告先驱

58．查尔斯·奥斯汀·贝茨 Charles Austin
Bates（1866-1936？）：广告文案的鼻祖

59．斯坦·弗雷伯格Stan Freberg（1926-2015 ）：讽刺幽默广告的开拓者

60. 鲁珀特·默多克 Rupert Murdoch（1931- ）：全球传媒帝国缔造者

61．哈里森·金·麦肯Harrison King McCann（1880-1962）：麦肯广告集团奠基人

62．伯尼斯·菲茨---吉本Bernice
Fitz-Gibbon（1894-1982）：零售广告的开拓创新者。

63．乔·塞德迈尔 Joe Sedelmaier（1933- ）：电视广告的幽默大王

64．西奥多·贝茨Theodore L. Bates（1901-1972）：达彼思广告（Ted Bates &
Co.）创建人

65．霍华德·齐夫Howard Zieff（1943- ）：电视广告的喜剧之王。

66．沃尔特·汤普森 J. Walter
Thompson（1847-1928）：智威汤逊广告（JWT）公司创立者。

67．罗伯特·雅各比 Robert Jacoby（1928-
）：卖达彼思广告公司而成为最富有的广告人之一。

68．亚瑟·戈弗雷Arthur Godfrey（1903-1983）：广播电视广告名星

69. 老尼尔森 A.C. Nielsen Sr.（1898-1980）：现代市场研究奠基人

70. 老詹姆斯·麦格劳 James H. McGraw
Sr.（1860-1948）：创建了国际出版公司麦格劳-希尔。

71．杰里·德拉·费明纳Jerry Della Femina（1936-
）：创意广告流派的代表人物之一，声称"超级碗就是审判日"。

72．本·达菲 Ben Duffy （1902-1970）：BBDO 总裁 新业务拓展高手

73．欧内斯特·埃莫·卡尔金斯Earnest Elmo
Calkins（1868-1964）：将设计美带入广告的先锋。

74．乔治·路易斯 George Lois（1931-2022
）：麦迪逊大道上特立独行的"坏小孩"

75．迈克尔·乔丹Michael Jordan（1963- ）：品牌（耐克等）代言人的标杆。

76．西奥多·瑞普利尔 Theodore （Ted）
Repplier（1889-1971）：著名广告组织活动家。

77．鲁恩·阿尔利奇 Roone
Arledge（1931-2002）：现代体育频道和体育营销的创新缔造者。

78．托马斯·伯勒尔Thomas J. Burrell（1939- ）：第一位黑人美国4A主席。

79. 小克雷恩 G.D. Crain
Jr.（1885-1973）：著名的《广告时代》（Advertising Age）创始人。

80．爱默生·富特 Emerson Foote（1906-1992）：著名的FCB联合创始人。

81．比尔·贝克 Bill Backer（1926-2016 ）：品牌广告和歌曲的顶级创意人。

82．乔·皮特卡 Joe Pytka（1938- ）：电视广告的一流大师。

83．费尔法克斯·科恩Fairfax Cone （1903-1977）：FCB
的联合创始人和博学多才的执行副总裁。

84．丹尼尔·斯达奇Daniel
Starch（1883-1979）：科学广告流派的重要人物，广告测试的先驱。

85．约翰·E．鲍尔斯John E.
Powers（1837-1919）：广告文案奠基者，被称为现代创意广告之父。

86．维克多·施瓦布 Victor O.
Schwab（1898-1980）：以测试改善广告文案的先行者

87．迈克尔·奥维茨Michael Ovitz（1946- ）：好莱坞最具影响力的广告人

88．塞勒斯·柯蒂斯Cyrus H.K.
Curtis（1850-1933）：创新现代杂志的出版人，美国富翁

89．霍华德·贝尔Howard H. Bell（1926-
）：美国广告联合会主席，建立广告法规的核心人物。

90．理查德·洛德Richard Lord（1926- ）：人格备受尊敬、屡获殊荣的广告人。

91．迈克尔·艾斯纳Michael Eisner（1942-
）：带领迪士尼成为顶级文旅品牌和多媒体巨头。

92．阿尔·阿亨鲍姆Al Achenbaum（1925- ）：建立广告商代理评估和帐户审查。

93．史蒂夫·法兰克福Steve Frankfurt（1931-2012 ）：Young &
Rubicam公司才华横溢的创意总监。

94．莱斯特·伟门Lester Wunderman（1920-2019 ）：直效行销之父

95．佩吉·查伦Peggy Charren（1928-2015 ）：《儿童电视法案》的主要推动者。

96．弗兰克·胡默特Frank Hummert（1879-1966）：广播肥皂剧及广告的开创者

97．山姆·维特Sam Vitt（1926- ）：独立媒体购买模式的开创者。

98．克里夫·弗里曼Cliff Freeman（1941-2021
）：以"牛肉在哪里"闻名的广告创意人。

99．万斯·帕卡德Vance
Packard（1914-1996）：以《隐蔽的劝说者》一书对广告和社会产生了极大的影响。

100．斯蒂芬·M．凯斯Stephen M. Case（1958- ）：美国在线（America
Online）创始人。

**来源: 名单依据广告时代(AdAge) 网上资料** "TOP 100 PEOPLE OF THE
CENTURY" **，**

**网址:https://adage.com/article/special-report-the-advertising-century/ad-age-advertising-century-top-100-people/140153**

            """
        , unsafe_allow_html=True)


def classic_ad():
    import streamlit as st

    st.write("# 附录3： 20世纪最成功的广告T0P100 👋")

    markdown_text =         """

1999年《广告时代》（AA)杂志评选出20世纪最成功的百強广告活动，入选广告需达到或通过以下三条标准之一：A、是否构成了广告或社会流行文化的分水岭；B、是否促进了新品类的形成或帮助客户品牌成为其所属行业的龙头；C、是否令人难以忘怀。榜单排名如下（品牌名称-广告语-
广告代理商及时间）：

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
（真实的感觉），FMR（Fallon McElligott Rice），1985 21.
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
bride\"

（总是伴娘，从未新娘），Lambert & Feasley，1923

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

            """
    html_content = markdown.markdown(markdown_text)
    st.html(html_content)

def classic_ad_md():
    import streamlit as st

    st.write("# 附录3： 20世纪最成功的广告T0P100 👋")

    st.markdown(
        """

1999年《广告时代》（AA)杂志评选出20世纪最成功的百強广告活动，入选广告需达到或通过以下三条标准之一：A、是否构成了广告或社会流行文化的分水岭；B、是否促进了新品类的形成或帮助客户品牌成为其所属行业的龙头；C、是否令人难以忘怀。榜单排名如下（品牌名称-广告语-
广告代理商及时间）：

1. 大众甲壳虫汽车(Volkswagen)，"think small"（从小处着眼），DDB，1959
![Think Small advertising campaign](https://en.wikipedia.org/wiki/File:Think_Small.jpg#/media/File:Think_Small.jpg)

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
（真实的感觉），FMR（Fallon McElligott Rice），1985 21.
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
bride\"

（总是伴娘，从未新娘），Lambert & Feasley，1923

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

            """
        , unsafe_allow_html=True)


def chat_lu():
    import streamlit as st

    # Show title and description.
    st.title("💬 和广告思想简史对话")
    st.write(
        ""
    )

    default_prompt = """

    """

    # system_prompt = st.sidebar.text_area("System Prompt", default_prompt, height=200)
    # seed_message = {"role": "system", "content": system_prompt}
    seed_message = {"role": "system", "content": ""}
    # endregion

    # region SESSION MANAGEMENT
    # Initialise session state variables
    if "generated" not in st.session_state:
        st.session_state["generated"] = []
    if "past" not in st.session_state:
        st.session_state["past"] = []
    if "messages" not in st.session_state:
        st.session_state["messages"] = [seed_message]
    if "model_name" not in st.session_state:
        st.session_state["model_name"] = []
    if "cost" not in st.session_state:
        st.session_state["cost"] = []
    if "total_tokens" not in st.session_state:
        st.session_state["total_tokens"] = []
    if "total_cost" not in st.session_state:
        st.session_state["total_cost"] = 0.0
    # endregion

    # Ask user for their OpenAI API key via `st.text_input`.
    # Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
    # via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
    # openai_api_key = st.text_input("OpenAI API Key", type="password")
    # if not openai_api_key:
    #     st.info("Please add your OpenAI API key to continue.", icon="🗝️")
    # else:

        # Create an OpenAI client.
        # client = OpenAI(api_key=openai_api_key)

        # Create a session state variable to store the chat messages. This ensures that the
        # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input("What is up?"):
        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate a response using the OpenAI API.
        try:
            completion = openai.ChatCompletion.create(
                engine=ENV["AZURE_OPENAI_CHATGPT_DEPLOYMENT"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                # stream=True,
            )
            response = completion.choices[0].message.content
        except openai.error.APIError as e:
            st.write(response)
            response = f"The API could not handle this content: {str(e)}"
        # st.session_state["messages"].append({"role": "assistant", "content": response})
        #
        # # Stream the response to the chat using `st.write_stream`, then store it in
        # # session state.
        # with st.chat_message("assistant"):
        #     response = st.write_stream(stream)
        # st.session_state.messages.append({"role": "assistant", "content": response})
        # Stream the response to the chat using `st.write_stream`, then store it in
        # session state.
        with st.chat_message("assistant"):
            # response = st.write_stream(stream)
            # response = st.write_stream(stream)
            st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})



def mapping_demo():
    import streamlit as st
    import pandas as pd
    import pydeck as pdk

    from urllib.error import URLError

    st.markdown(f"# {list(page_names_to_funcs.keys())[2]}")
    st.write(
        """
        This demo shows how to use
[`st.pydeck_chart`](https://docs.streamlit.io/develop/api-reference/charts/st.pydeck_chart)
to display geospatial data.
"""
    )

    @st.cache_data
    def from_data_file(filename):
        url = (
                "http://raw.githubusercontent.com/streamlit/"
                "example-data/master/hello/v1/%s" % filename
        )
        return pd.read_json(url)

    try:
        ALL_LAYERS = {
            "Bike Rentals": pdk.Layer(
                "HexagonLayer",
                data=from_data_file("bike_rental_stats.json"),
                get_position=["lon", "lat"],
                radius=200,
                elevation_scale=4,
                elevation_range=[0, 1000],
                extruded=True,
            ),
            "Bart Stop Exits": pdk.Layer(
                "ScatterplotLayer",
                data=from_data_file("bart_stop_stats.json"),
                get_position=["lon", "lat"],
                get_color=[200, 30, 0, 160],
                get_radius="[exits]",
                radius_scale=0.05,
            ),
            "Bart Stop Names": pdk.Layer(
                "TextLayer",
                data=from_data_file("bart_stop_stats.json"),
                get_position=["lon", "lat"],
                get_text="name",
                get_color=[0, 0, 0, 200],
                get_size=15,
                get_alignment_baseline="'bottom'",
            ),
            "Outbound Flow": pdk.Layer(
                "ArcLayer",
                data=from_data_file("bart_path_stats.json"),
                get_source_position=["lon", "lat"],
                get_target_position=["lon2", "lat2"],
                get_source_color=[200, 30, 0, 160],
                get_target_color=[200, 30, 0, 160],
                auto_highlight=True,
                width_scale=0.0001,
                get_width="outbound",
                width_min_pixels=3,
                width_max_pixels=30,
            ),
        }
        st.sidebar.markdown("### Map Layers")
        selected_layers = [
            layer
            for layer_name, layer in ALL_LAYERS.items()
            if st.sidebar.checkbox(layer_name, True)
        ]
        if selected_layers:
            st.pydeck_chart(
                pdk.Deck(
                    map_style="mapbox://styles/mapbox/light-v9",
                    initial_view_state={
                        "latitude": 37.76,
                        "longitude": -122.4,
                        "zoom": 11,
                        "pitch": 50,
                    },
                    layers=selected_layers,
                )
            )
        else:
            st.error("Please choose at least one layer above.")
    except URLError as e:
        st.error(
            """
            **This demo requires internet access.**

            Connection error: %s
        """
            % e.reason
        )


def plotting_demo():
    import streamlit as st
    import time
    import numpy as np

    st.markdown(f'# {list(page_names_to_funcs.keys())[1]}')
    st.write(
        """
        This demo illustrates a combination of plotting and animation with
Streamlit. We're generating a bunch of random numbers in a loop for around
5 seconds. Enjoy!
"""
    )

    progress_bar = st.sidebar.progress(0)
    status_text = st.sidebar.empty()
    last_rows = np.random.randn(1, 1)
    chart = st.line_chart(last_rows)

    for i in range(1, 101):
        new_rows = last_rows[-1, :] + np.random.randn(5, 1).cumsum(axis=0)
        status_text.text("%i%% Complete" % i)
        chart.add_rows(new_rows)
        progress_bar.progress(i)
        last_rows = new_rows
        time.sleep(0.05)

    progress_bar.empty()

    # Streamlit widgets automatically run the script from top to bottom. Since
    # this button is not connected to any other logic, it just causes a plain
    # rerun.
    st.button("Re-run")


def plotting_data():
    import streamlit as st
    import time
    import numpy as np

    st.markdown(f'# {list(page_names_to_funcs.keys())[1]}')
    st.write(
        """
        自1919年以来美国年度广告支出 ( GDP的单位为10亿美金 )
"""
    )


    data = {
        '年度': [1919, 1920, 1921, 1922, 1923, 1924, 1925, 1926, 1927, 1928, 1929, 1930, 1931, 1932, 1933, 1934, 1935,
                 1936, 1937, 1938, 1939, 1940, 1941, 1942, 1943, 1944, 1945, 1946, 1947, 1948, 1949, 1950, 1951, 1952,
                 1953, 1954, 1955, 1956, 1957, 1958, 1959, 1960, 1961, 1962, 1963, 1964, 1965, 1966, 1967, 1968, 1969,
                 1970, 1971, 1972, 1973, 1974, 1975, 1976, 1977, 1978, 1979, 1980, 1981, 1982, 1983, 1984, 1985, 1986,
                 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003,
                 2004, 2005, 2006, 2007],
        '广告总支出': [1930, 2480, 1930, 2200, 2400, 2480, 2600, 2700, 2720, 2760, 2850, 2450, 2100, 1620, 1325, 1650,
                       1720,
                       1930, 2100, 1930, 2010, 2110, 2250, 2160, 2490, 2700, 2840, 3340, 4260, 4870, 5210, 5700, 6420,
                       7140,
                       7740, 8150, 9150, 9910, 10270, 10310, 11270, 11960, 11860, 12430, 13100, 14150, 15250, 16630,
                       16870,
                       18090, 19420, 19550, 20700, 23210, 24980, 26620, 27900, 33300, 37440, 43330, 48780, 53570, 60460,
                       66670, 76000, 88010, 94900, 102370, 110270, 118750, 124770, 129968, 128352, 133750, 140956,
                       153024,
                       162930, 175230, 187529, 206697, 222308, 247472, 231287, 236875, 245477, 263766, 271074, 281653,
                       279612],
        '报刊广播电视的广告支出': [733, 830, 940, 1017, 1101, 1188, 1281, 1355, 1432, 1493, 1560, 1378, 1220, 1000, 832,
                                   935,
                                   1065, 1191, 1305, 1182, 1232, 1311, 1400, 1352, 1639, 1790, 1923, 2262, 2723, 3091,
                                   3301,
                                   3633, 4080, 4552, 4942, 5161, 5866, 6342, 6588, 6509, 7183, 7585, 7510, 7896, 8284,
                                   9018,
                                   9761, 10734, 10887, 11718, 12723, 12702, 13293, 14921, 16042, 17009, 17935, 21579,
                                   24470,
                                   28322, 31954, 34937, 39167, 42811, 49057, 56765, 60663, 65029, 69141, 74004, 77841,
                                   79932,
                                   76997, 80560, 84570, 92501, 97622, 105973, 113221, 123628, 132151, 145887, 132296,
                                   136244,
                                   140128, 150305, 151939, 155466, 150023],
        'GDP': [78.3, 88.4, 73.6, 73.4, 85.4, 87.0, 90.6, 97.0, 95.5, 97.4,
                103.6, 91.2, 76.5, 58.7, 56.4, 66.0, 73.3, 83.8, 91.9, 86.1,
                92.2, 101.4, 126.7, 161.9, 198.6, 219.8, 223.1, 222.3, 244.2,
                269.2, 267.3, 293.8, 339.3, 358.3, 379.4, 380.4, 414.8, 437.5,
                461.1, 467.2, 506.6, 526.4, 544.7, 585.6, 617.7, 663.6, 719.1,
                787.8, 832.6, 910.0, 984.6, 1038.5, 1127.1, 1238.3, 1382.7,
                1500.0, 1638.3, 1825.3, 2030.9, 2294.7, 2563.3, 2789.5, 3128.4,
                3255.0, 3536.7, 3933.2, 4220.3, 4462.8, 4739.5, 5103.8, 5484.4,
                5803.1, 5995.9, 6337.7, 6657.4, 7072.2, 7397.7, 7816.9, 8304.3,
                8747.0, 9268.4, 9817.0, 10128.0, 10470.0, 10961.0, 11713.0,
                12456.0, 13178.0, 13807.0],
        'Ads as % of GDP': [2.5, 2.8, 2.6, 3.0, 2.8, 2.9, 2.9, 2.8, 2.8, 2.8, 2.8, 2.7, 2.7, 2.8, 2.3, 2.5, 2.3, 2.3,
                            2.3, 2.2, 2.2, 2.1, 1.8, 1.3, 1.3, 1.2, 1.3, 1.5, 1.7, 1.8, 1.9, 1.9, 1.9, 2.0, 2.0, 2.1,
                            2.2, 2.3, 2.2, 2.2, 2.2, 2.3, 2.2, 2.1, 2.1, 2.1, 2.1, 2.1, 2.0, 2.0, 2.0, 1.9, 1.8, 1.9,
                            1.8, 1.8, 1.7, 1.8, 1.8, 1.9, 1.9, 1.9, 1.9, 2.0, 2.1, 2.2, 2.2, 2.3, 2.3, 2.3, 2.2, 2.1,
                            2.1, 2.1, 2.1, 2.2, 2.2, 2.2, 2.3, 2.4, 2.4, 2.5, 2.3, 2.3, 2.2, 2.3, 2.2, 2.1, 2.0]
    }

    # Create a DataFrame from the dictionary
    df = pd.DataFrame(data)
    # df.set_index('年度', inplace=True)
    df.set_index('年度')

    progress_bar = st.sidebar.progress(0)
    status_text = st.sidebar.empty()
    last_rows = df.head(1)
    chart = st.line_chart(last_rows, x="年度", ｙ=["广告总支出", "报刊广播电视的广告支出", "GDP"], y_label="单位:百万美元",
                  x_label="自1919年以来美国年度广告支出 ( GDP的单位为10亿美金 )")

    for i in range(1, len(df)+1):
        new_rows = df.iloc[:i]
        status_text.text("%i%% Complete" % i)
        chart.add_rows(new_rows)
        progress_bar.progress(i)
        time.sleep(0.05)

    progress_bar.empty()

    # Streamlit widgets automatically run the script from top to bottom. Since
    # this button is not connected to any other logic, it just causes a plain
    # rerun.
    st.button("Re-run")

    # st.line_chart(df, x="年度", ｙ=["广告总支出", "报刊广播电视的广告支出", "GDP"], y_label="单位:百万美元",
    #               x_label="自1919年以来美国年度广告支出 ( GDP的单位为10亿美金 )")


def plotting_data_v1():
    import streamlit as st
    import time
    import numpy as np

    st.markdown(f'# {list(page_names_to_funcs.keys())[1]}')
    st.write(
        """
        This demo illustrates a combination of plotting and animation with
Streamlit. We're generating a bunch of random numbers in a loop for around
5 seconds. Enjoy!
"""
    )


    data = {
        '年度': [1919, 1920, 1921, 1922, 1923, 1924, 1925, 1926, 1927, 1928, 1929, 1930, 1931, 1932, 1933, 1934, 1935,
                 1936, 1937, 1938, 1939, 1940, 1941, 1942, 1943, 1944, 1945, 1946, 1947, 1948, 1949, 1950, 1951, 1952,
                 1953, 1954, 1955, 1956, 1957, 1958, 1959, 1960, 1961, 1962, 1963, 1964, 1965, 1966, 1967, 1968, 1969,
                 1970, 1971, 1972, 1973, 1974, 1975, 1976, 1977, 1978, 1979, 1980, 1981, 1982, 1983, 1984, 1985, 1986,
                 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003,
                 2004, 2005, 2006, 2007],
        '广告总支出': [1930, 2480, 1930, 2200, 2400, 2480, 2600, 2700, 2720, 2760, 2850, 2450, 2100, 1620, 1325, 1650,
                       1720,
                       1930, 2100, 1930, 2010, 2110, 2250, 2160, 2490, 2700, 2840, 3340, 4260, 4870, 5210, 5700, 6420,
                       7140,
                       7740, 8150, 9150, 9910, 10270, 10310, 11270, 11960, 11860, 12430, 13100, 14150, 15250, 16630,
                       16870,
                       18090, 19420, 19550, 20700, 23210, 24980, 26620, 27900, 33300, 37440, 43330, 48780, 53570, 60460,
                       66670, 76000, 88010, 94900, 102370, 110270, 118750, 124770, 129968, 128352, 133750, 140956,
                       153024,
                       162930, 175230, 187529, 206697, 222308, 247472, 231287, 236875, 245477, 263766, 271074, 281653,
                       279612],
        '报刊广播电视的广告支出': [733, 830, 940, 1017, 1101, 1188, 1281, 1355, 1432, 1493, 1560, 1378, 1220, 1000, 832,
                                   935,
                                   1065, 1191, 1305, 1182, 1232, 1311, 1400, 1352, 1639, 1790, 1923, 2262, 2723, 3091,
                                   3301,
                                   3633, 4080, 4552, 4942, 5161, 5866, 6342, 6588, 6509, 7183, 7585, 7510, 7896, 8284,
                                   9018,
                                   9761, 10734, 10887, 11718, 12723, 12702, 13293, 14921, 16042, 17009, 17935, 21579,
                                   24470,
                                   28322, 31954, 34937, 39167, 42811, 49057, 56765, 60663, 65029, 69141, 74004, 77841,
                                   79932,
                                   76997, 80560, 84570, 92501, 97622, 105973, 113221, 123628, 132151, 145887, 132296,
                                   136244,
                                   140128, 150305, 151939, 155466, 150023],
        'GDP': [78.3, 88.4, 73.6, 73.4, 85.4, 87.0, 90.6, 97.0, 95.5, 97.4,
                103.6, 91.2, 76.5, 58.7, 56.4, 66.0, 73.3, 83.8, 91.9, 86.1,
                92.2, 101.4, 126.7, 161.9, 198.6, 219.8, 223.1, 222.3, 244.2,
                269.2, 267.3, 293.8, 339.3, 358.3, 379.4, 380.4, 414.8, 437.5,
                461.1, 467.2, 506.6, 526.4, 544.7, 585.6, 617.7, 663.6, 719.1,
                787.8, 832.6, 910.0, 984.6, 1038.5, 1127.1, 1238.3, 1382.7,
                1500.0, 1638.3, 1825.3, 2030.9, 2294.7, 2563.3, 2789.5, 3128.4,
                3255.0, 3536.7, 3933.2, 4220.3, 4462.8, 4739.5, 5103.8, 5484.4,
                5803.1, 5995.9, 6337.7, 6657.4, 7072.2, 7397.7, 7816.9, 8304.3,
                8747.0, 9268.4, 9817.0, 10128.0, 10470.0, 10961.0, 11713.0,
                12456.0, 13178.0, 13807.0],
        'Ads as % of GDP': [2.5, 2.8, 2.6, 3.0, 2.8, 2.9, 2.9, 2.8, 2.8, 2.8, 2.8, 2.7, 2.7, 2.8, 2.3, 2.5, 2.3, 2.3,
                            2.3, 2.2, 2.2, 2.1, 1.8, 1.3, 1.3, 1.2, 1.3, 1.5, 1.7, 1.8, 1.9, 1.9, 1.9, 2.0, 2.0, 2.1,
                            2.2, 2.3, 2.2, 2.2, 2.2, 2.3, 2.2, 2.1, 2.1, 2.1, 2.1, 2.1, 2.0, 2.0, 2.0, 1.9, 1.8, 1.9,
                            1.8, 1.8, 1.7, 1.8, 1.8, 1.9, 1.9, 1.9, 1.9, 2.0, 2.1, 2.2, 2.2, 2.3, 2.3, 2.3, 2.2, 2.1,
                            2.1, 2.1, 2.1, 2.2, 2.2, 2.2, 2.3, 2.4, 2.4, 2.5, 2.3, 2.3, 2.2, 2.3, 2.2, 2.1, 2.0]
    }

    # Create a DataFrame from the dictionary
    df = pd.DataFrame(data)
    df
    # df.set_index('年度', inplace=True)
    df.set_index('年度')

    progress_bar = st.sidebar.progress(0)
    status_text = st.sidebar.empty()
    last_rows = df.head(1)
    chart = st.line_chart(last_rows)

    # for i in range(1, len(df)+1):
    #     new_rows = df.iloc[i]
    #     status_text.text("%i%% Complete" % i)
    #     chart.add_rows(new_rows)
    #     progress_bar.progress(i)
    #     last_rows = new_rows
    #     time.sleep(0.05)
    #
    # progress_bar.empty()
    #
    # # Streamlit widgets automatically run the script from top to bottom. Since
    # # this button is not connected to any other logic, it just causes a plain
    # # rerun.
    # st.button("Re-run")


    st.line_chart(df, x="年度", ｙ=["广告总支出", "报刊广播电视的广告支出", "GDP"], y_label="单位:百万美元",
                  x_label="自1919年以来美国年度广告支出 ( GDP的单位为10亿美金 )")




page_names_to_funcs = {
    "首页": intro,
    "广告大事年表": memorabilia,
    "20世纪广告百位巨星榜": superstar,
    "20世纪最成功的广告T0P100": classic_ad,
    "行业数据": plotting_data,
    "与大师对话": chat_lu
}

demo_name = st.sidebar.selectbox("请选择", page_names_to_funcs.keys())
page_names_to_funcs[demo_name]()
