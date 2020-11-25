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

    // 2. 点击保存按钮
    $('.box-footer button.save').click(function(){      // 用$this必须用function,不能用()=>
        $
            .ajax({
                url: $(this).data('url'),
                data: $('form').serialize(),
                type: $(this).data('type')
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
    });

    // 3. 复选框逻辑
    // 点击一级菜单，二级菜单联动
    // 勾选一级菜单，二级菜单全选，取消一级菜单，二级菜单全取消
    $('div.checkbox.one').each(function(){
        let $this = $(this);        // this -- > div
        $this.find(':checkbox').click(function(){
            if($(this).is(':checked')){            // this -- > checkbox
                // 选中状态
                $this.siblings('div.checkbox.two').find(':checkbox').prop('checked', true)
            }else{
                // 取消状态
                $this.siblings('div.checkbox.two').find(':checkbox').prop('checked', false)
            }
        })
    });

    // 点击二级菜单，一级菜单联动
    // 选中二级菜单，对应的一级菜单选中，二级菜单全部取消，一级菜单自动取消
    $('div.checkbox.two').each(function(){
        let $this = $(this);
        $this.find(':checkbox').click(function(){
            if($(this).is(':checked')){
                // 选中
                $this.siblings('div.checkbox.one').find(':checkbox').prop('checked', true)
            }else{
                if(!$this.siblings('div.checkbox.two').find(':checkbox').is(':checked')){
                    $this.siblings('div.checkbox.one').find(':checkbox').prop('checked', false)
                }
            }
        })
    });
})