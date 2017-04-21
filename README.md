# iflasky
Study "Flask Web Development", code cases for some chapters
***
## 中文说明
### 目的
本仓库的目的是记录学习《Flask Web开发》过程中，对照每节所讲理解后动手编写的代码。大部分与书中一样，但是仍存在一些修改，集中在逻辑和显示。所做的修改主要希望能更符合生产的要求，参照了一些网站的设计。修改后也可能存在很多不足，希望大家包容和指正。

### 改动
* 点击找回密码的链接后，无需再输Email地址，直接输入新密码即可
* 放宽对Markdown标签和属性的限制
* 不提倡用户可以更换邮箱，用户的邮箱只能通过管理员才能更换
* 增加文章标题，文章摘要
* 重新布局关注者和被关注者页面
* 对显示关注者和自己文章的标签页，通过添加查询来完成，避免大量不必要改动（如：自己关注自己）。同时也发现，可能必须指定“pagination.total = query.count()”，否则该分页会出现错误，目前不清楚是否为bug
* 管理评论部分，将修改评论状态的两个函数合并为一个
* 修复当输入为连续的英文字母或数字时，文章和评论不换行的问题
* 增加Redis缓存系统，减少页面响应时间

### 安装
<code>wget http://download.redis.io/redis-stable.tar.gz</code>   

<code>tar xvzf redis-stable.tar.gz</code>   

<code>cd redis-stable</code>   

<code>make</code>   

<code>make install</code>

### 运行
<code>redis-server</code>   

<code>./manage.py runserver</code>