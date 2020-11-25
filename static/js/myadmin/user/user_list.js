$(()=>{
    // 获取查询表单
    let $queryForm = $('form.user-query');
    // 分页
    let $pageLi = $('ul.pagination li').not('.active').not('.disabled');   // 去掉当前页和不可点击的按钮

    $pageLi.click(function(){
        let $this = $(this);
        $
            .ajax({
                url: $('.sidebar-menu li.active a').data('url'),
                data: $queryForm.serialize() + '&page=' + $this.data('page'),
                type: 'GET'
            })
            .done((res)=>{
                $('#content').html(res)
            })
            .fail(()=>{
                message.showError('服务器超时，请重试！')
            })
    })

    // 查询、重置按钮js
    let $queryBtn = $('form.user-query button.query');     // 查询按钮
    let $resetBtn = $('form.user-query button.reset');     // 重置按钮

    $queryBtn.click(function(){
        $
            .ajax({
                url: $('.sidebar-menu li.active a').data('url'),
                data: $queryForm.serialize(),
                type: 'GET'
            })
            .done((res)=>{
                $('#content').html(res)
            })
            .fail(()=>{
                message.showError('服务器超时，请重试！')
            })
    })

    $resetBtn.click(function(){
        $queryForm[0].reset();
        $
            .ajax({
                url: $('.sidebar-menu li.active a').data('url'),
                type: 'GET'
            })
            .done((res)=>{
                $('#content').html(res)
            })
            .fail(()=>{
                message.showError('服务器超时，请重试！')
            })
    })

    // 用户详情
    $('tr').each(function(){
        $(this).children('td').click(function(){      // 点击记录的每一个单元格都可以跳转到详情页
            $('#content').load(
                '/myadmin/user/' + $(this).children('a').data('id') + '/',
                (response, status, xhr) =>{
                    if (status !== 'success'){
                        message.showError('服务器超时，请重试！')
                    }
                }
            )

        })
    })
})