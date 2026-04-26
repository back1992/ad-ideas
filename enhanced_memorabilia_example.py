"""
Enhanced Memorabilia Page with Feedback Integration

This is an example of how to integrate the feedback system
into existing content pages.
"""

import streamlit as st
from modules.database import get_database_manager
from modules.auth import get_auth_manager
from modules.feedback import get_feedback_system, get_feedback_display_components


def enhanced_memorabilia():
    """Enhanced version of memorabilia page with feedback integration."""
    
    st.write("# 附录1 ：广告大事年表 👋")
    
    # Initialize systems for feedback
    db_manager = get_database_manager()
    auth_manager = get_auth_manager(db_manager=db_manager)
    feedback_system = get_feedback_system(db_manager)
    display_components = get_feedback_display_components(feedback_system)
    
    st.markdown("""
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
    """)
    
    # Add feedback section
    st.markdown("---")
    st.markdown("### 💭 您对这个时间线内容的看法")
    
    # Check if user is logged in
    if st.session_state.get('authentication_status'):
        # Show feedback collection interface
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 👍 快速评价")
            display_components.display_thumbs_feedback(
                target_type="timeline",
                target_id="advertising_memorabilia_15_19_century",
                show_collection=True
            )
        
        with col2:
            st.markdown("#### ⭐ 详细评分")
            display_components.display_stars_feedback(
                target_type="timeline",
                target_id="advertising_memorabilia_15_19_century",
                show_collection=True
            )
    
    else:
        # Show statistics only for non-logged users
        st.info("登录后可以对内容进行评价和反馈")
        
        # Still show existing feedback statistics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 用户评价统计")
            feedback_system.show_feedback_stats("timeline", "advertising_memorabilia_15_19_century")
        
        with col2:
            st.markdown("#### 🔥 相关热门内容")
            display_components.display_trending_content("timeline", 3)


if __name__ == "__main__":
    enhanced_memorabilia()