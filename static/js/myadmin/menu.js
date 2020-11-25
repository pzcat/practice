$(()=>{
    let $sideBar = $('.sidebar-menu');          // 边栏url
    let $bars = $('.sidebar-menu').find('li:not(.treeview)');    // 所有可点击的菜的条目 not(.treeview)排除父菜单

    $bars.click(function(){
        $this = $(this);             // 获取被点击的对象

        // 被点击的对象强调显示
        $bars.removeClass('active');
        $this.addClass('active');

        // 点击某个一级菜单，其他的一级菜单的子菜单收缩
        // jq对象不能比较 $this.parent === $sideBar，要转换成dom对象
        // 方法二if ($this.hasClass('treeview'))
        if($this.parent()[0] === $sideBar[0]){
            // 关闭打开的二级菜单
            // 通过 li.treeview.menu-open定位到打开的一级菜单，.children('ul')找到要收缩的对象，slideup()方法实现向上收起
            $sideBar.children('li.treeview.menu-open').children('ul').slideUp();
            $sideBar.children('li.treeview.menu-open').removeClass('menu-open');
        }

        // 发送ajax，动态修改content
        $('#content').load(
            $this.children('a:first').data('url'),
            (response, status, xhr)=>{
                if(status !== 'success'){
                    message.showError('服务器超时，请重试！')
                }
            }
        );

    });

    // 首次访问激活第一个菜单内容
    $bars[0].click();

    // csrf_token
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });
})