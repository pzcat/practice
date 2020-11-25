$(()=>{
    // 1. 点击返回，回到用户列表页面（和点击用户管理菜单效果相同）
    $('.box-footer button.back').click(()=>{
        $('#content').load(
            $('.sidebar-menu li.active a').data('url'),
            (response, status, xhr) =>{
                if (status !== 'success'){
                    message.showError('服务器超时，请重试！');
                }
            }
        );
    });
    // 2. 点击修改按钮
    $('.box-footer button.save').click(function(){      // 用$this必须用function,不能用()=>
        $
            .ajax({
                url: $(this).data('url'),
                data: $('form').serialize(),
                type: 'PUT'
            })
            .done((res)=>{
                if(res.errno === '0'){
                    message.showSuccess(res.errmsg);
                    // 跳转到用户列表
                    $('#content').load(
                        $('.sidebar-menu li.active a').data('url'),
                        (response, status, xhr) =>{
                            if (status !== 'success'){
                                message.showError('服务器超时，请重试！');
                            }
                        }
                    );
                }else{
                    $('#content').html(res)
                }
            })
            .fail(()=>{
                message.showError('服务器超时，请重试！')
        })  ;
    })

})