
$(function(){
    /*=== bannerStart ===*/
    // 轮播图
    // 1. 加载轮播图数据
    function fn_load_banner(){
        // 发送Ajax 获取数据
        $
            .ajax({
                url: '/news/banners/',
                type: 'GET',
                dataType: 'json',
                async: false               // 默认为异步，由于我们需要加载主页时立即渲染，设置为同步: false
            })
            .done((res)=>{
                if (res.errno ==='0'){
                    let content = '';
                    let tab_content = '';
                    res.data.banners.forEach((one_banner, index) => {
                        if (index === 0) {
                            // 第一页加active属性
                            content = `
                                <li style="display:block;">
                                    <a href="/news/${one_banner.news_id}/">
                                        <img src="${one_banner.image_url}" alt="${one_banner.news_title}">
                                    </a>
                                </li>`;
                            tab_content = `<li class="active">`;
                        } else {
                            content = `
                                <li>
                                    <a href="/news/${one_banner.news_id}/">
                                        <img src="${one_banner.image_url}" alt="${one_banner.news_title}">
                                    </a>
                                </li>`;
                            tab_content = `<li></li>`;
                        }
                        $('.pic').append(content);
                        $('.tab').append(tab_content);
                    })
                } else {
                    message.showError(res.errmsg)
                }
            })
            .fail(()=>{
                message.showError('服务器超时，请重试')
            })
    }

    fn_load_banner();
    // 定义变量
    let $banner = $('.banner');               // banner div
    let $picLi = $('.banner .pic li');         // 图片li标签
    let $pre = $('.banner .prev');            // 上一张
    let $next = $('.banner .next');           // 下一张
    let $tabLi = $('.banner .tab li');        // 按钮
    let index = 0;

    // 2. 点击导航按钮切换
    $tabLi.click(function () {
        index = $(this).index();
        $(this).addClass('active').siblings('li').removeClass('active');
        $picLi.eq(index).fadeIn(1500).siblings('li').fadeOut(1500);
    });

    // 3. 点击左右箭头切换
    // 点击切换上一张
    $pre.click(()=>{
        index --;
        if (index < 0){
            index = $tabLi.length - 1           // 最后一张
        }
        $tabLi.eq(index).addClass('active').siblings('li').removeClass('active');
        $picLi.eq(index).fadeIn(1500).siblings('li').fadeOut(1500);
    });

    // 点击切换下一张
    $next.click(()=>{
        auto();
    });

    // 图片向前滑动
    function auto(){
        index ++;
        index %= $tabLi.length;
        $tabLi.eq(index).addClass('active').siblings('li').removeClass('active');
        $picLi.eq(index).fadeIn(1500).siblings('li').fadeOut(1500);
    }

    // 4. 定时切换
    let timer = setInterval(auto, 2500);

    // 5. 鼠标悬停暂停切换
    $banner.hover(
        ()=>{
            clearInterval(timer)
        },
        ()=>{
            timer = setInterval(auto,2500);
        }
    )

    /*=== bannerEnd ===*/

    /*=== newsNavStart ===*/
    // 新闻列表
    let $newNavLi = $('.news-nav ul li');            // 标签li
    let iPage = 1;                                   // 默认第一页
    let iTotalPage = 1;                              // 默认总页数为1页
    let iCurrentTagId = 0;                           // 默认分类标签为0
    let bIsLoadData = true;                          // 是否正在向后台加载数据

    fn_load_content();

    // 点击分类标签
    $newNavLi.click(function(){
        // 点击分类标签，则为点击的标签加上class=active的属性
        // 同时移除其他兄弟元素上的active属性
        $(this).addClass('active').siblings('li').removeClass('active');
        // 获取绑定在data-id属性上个的tag_id
        let iClickTagId = $(this).children('a').attr('data-id');
        if (iClickTagId !== iCurrentTagId){
            iCurrentTagId = iClickTagId;       // 记录当前分类id
            // 重置分页参数
            iPage = 1;
            iTotalPage = 1;
            fn_load_content();
        }
    })
    /*=== newsNavEnd ===*/
    // 页面滚动加载
    $(window).scroll(function(){
        // 浏览器窗口高度
        let showHeight = $(window).height();
        // 整个网页高度
        let pageHeight = $(document).height();
        // 页面可以滚动的距离
        let canScrollHeight = pageHeight - showHeight;
        // 页面滚动了多少，整个是随着页面滚动实时变化的
        let nowScroll = $(document).scrollTop();
        if ((canScrollHeight - nowScroll) < 100){
            if (!bIsLoadData){
                bIsLoadData = true;
                // 判断页数，去更新新闻，小于总数才加载
                if (iPage < iTotalPage){
                    iPage += 1;
                    fn_load_content();
                } else {
                    message.showInfo('已全部加载，没有更多内容');
                    $('a.btn-more').html('已全部加载，没有更多内容');
                }
            }
        }
    })

    // 向后端获取新闻列表数据
    function fn_load_content(){
        $.ajax({
            url: '/news/',
            type: 'GET',
            data: {
                tag: iCurrentTagId,
                page: iPage
            },
            dataType: 'json',
            success: function(res){
                if (res.errno === '0') {
                    iTotalPage = res.data.total_pages;
                    if (iPage ===1){
                        // 第一页清空内容--不同新闻标签切换时
                        $('.news-list').html('')
                    }
                    res.data.news.forEach(function (one_news){
                        let content = `
                            <li class="news-item">
                                <a href="/news/${one_news.id}/" class="news-thumbnail" target="_blank">
                                    <img src="${one_news.image_url}" alt="${one_news.title}" title="{one_news.title}">
                                </a>
                                <div class="news-content">
                                    <h4 class="news-title">
                                        <a href="/news/${one_news.id}/">${one_news.title}</a>
                                    </h4>
                                    <p class="news-details">${one_news.digest}</p>
                                    <div class="news-other">
                                        <span class="news-type">${one_news.tag_name}</span>
                                        <span class="news-time">${one_news.update_time}</span>
                                        <span class="news-author">${one_news.author}</span>
                                    </div>
                                </div>
                            </li>
                        `;
                        $('.news-list').append(content);
                    });
                    // 数据加载完毕，设置正在加载数据变量为false
                    bIsLoadData = false;
                    $('a.btn-more').html('滚动加载更多');
                }else{
                    // 加载失败，打印错误信息
                    message.showError(res.errmsg);
                }
            },
            error: function () {
                message.showError('服务器超时，请重试！');
            }
        });
    }
});




$(()=>{
    let $newsLi = $('.news-nav ul li');
    $newsLi.click(function(event) {
        $(this).addClass('active').siblings('li').removeClass('active');
    });
});


