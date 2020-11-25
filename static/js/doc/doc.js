$(()=>{
    let iPage = 1;
    let iTotalPage = 1;
    let bIsLoadData = false;

    fn_load_docs();     // 加载文件列表
    // 页面滚动加载
    $(window).scroll(function(){
        // 浏览器窗口高度
        let showHeight = $(window).height();
        // 整个页面高度
        let pageHeight = $(document).height();
        // 页面可以滚动的距离
        let canScrollHeight = pageHeight - showHeight;
        // 页面滚动了多少
        let nowScroll = $(document).scrollTop();
        if ((canScrollHeight - nowScroll) < 100){
            if (!bIsLoadData){
                bIsLoadData = true;
                // 判断页数，去更新新闻，小于总页数才加载
                if (iPage < iTotalPage){
                    iPage +=1;
                    fn_load_docs();
                }else {
                    message.showInfo('我也是有底线的~~');
                    $('a.btn-more').html('已全部加载，没有更多内容！')
                }
            }
        }
    });

    // 获取docs信息
    function fn_load_docs(){
        $
            .ajax({
                url: '/doc/docs/',
                type: 'GET',
                data: {page: iPage},
                dataType: 'json'
            })
            .done((res)=>{
                if (res.errno ==='0'){
                    iTotalPage = res.data.total_page;
                    res.data.docs.forEach((doc)=>{
                        let content = `
                        <li class="pay-item">
                            <div class="pay-img doc"></div>
                            <img src="${doc.image_url}" alt="" class="pay-img doc">
                            <div class="d-contain" >
                                <p class="doc-title">${doc.title}</p>
                                <p class="doc-desc">${doc.desc}</p>
                                <a href="${doc.file_url}" class="pay-price" download="${doc.file_name}">下载</a>
                            </div>   
                        </li>
                        `;
                        $('.pay-list').append(content);
                        bIsLoadData = false;
                        $('a.btn-more').html('滚动加载更多');
                    })
                }
            })
            .fail(()=>{
                message.showError('服务器超时，请重试！');
            })
    }
})