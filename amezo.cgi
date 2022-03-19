#!/usr/bin/perl
require 'jcode.pl';

$copyright = <<EOL;
<!-- 
     Script for amezo-like BBS
     Copyright (C) 1999-2000 amezo_
     http://www17.big.or.jp/~amezo_/
-->
EOL

$amezo = '＠あめぞう(仮)';
$urlbase = 'http://www17.big.or.jp/~amezo_/';
$admin = 'サポート';

$ENV{'SCRIPT_FILENAME'} =~ /\/([^\/]+)$/;
$cgi = $1;
if($ENV{'REQUEST_METHOD'} eq 'GET'){
	print "Content-type: text/plain\n\n";
	open(R, "./$cgi");
	print while <R>;
	close(R);
	exit;
}

read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
length($buffer) > 5000 && &error('投稿内容が大きすぎます');
$referer = $ENV{'HTTP_REFERER'};
$referer =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
$referer =~ /^$urlbase([\w\.\-]+)/ || &error('エラー');
$folder = $1;

@pairs = split(/&/,$buffer);
foreach $pair (@pairs) {
	($name, $value) = split(/=/, $pair);
	$value =~ tr/+/ /;
	$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
	&jcode'convert(*value,'sjis');
	$value =~ s/&/&amp;/g;
	$value =~ s/\"/&quot;/g;
	$value =~ s/</&lt;/g;
	$value =~ s/>/&gt;/g;
	$value =~ s/\r\n/\r/g;
	$value =~ s/\n/\r/g;
	$value =~ s/\r/<br>/g;
	$form{$name} = $value;
}

$name = $form{'name'};
$mail = $form{'mail'};
$comm = $form{'comm'};
$subj = $form{'subj'};
$folder = $form{'folder'} if $form{'folder'};
$res = $form{'res'};
$form{'sub'} && &res;
$next = $form{'next'};
$next = 1 if !$next;
$next += 20;
$reload = 1 if $name eq $subj && $name eq $comm;
$reload = 1 unless $name || $subj || $comm;
@a = ($comm =~ /<br>/g);
(@a + 0 > 20 || $comm =~ /￣￣/) && &error("コメントが長すぎます");
$name =~ s/ |　//g;
$x = $subj.$name.$comm;
$x =~ /山/ && $x =~ /本/ && ($subj =~ s/山//g, $name =~ s/山//g, $comm =~ s/山//g);
$x =~ /隆/ && $x =~ /雄/ && ($subj =~ s/隆//g, $name =~ s/隆//g, $comm =~ s/隆//g);

if($next == 21 && !$reload){

$_ = $admin;
s/(\W)/\\$1/g;
$name =~ s/$_/＃$admin/g;

crypt($name, 'am') eq 'amsqKfBaSfYYU' && &del;
$res && undef $subj;
$name || &error('投稿者を記入してください.');
$comm || &error("コメントが入力されていません");
$res || $subj || &error("題名が入力されていません");

$comm =~ s/(http\:[\w\.\~\-\/\?\+\=\:\@\%\;\#]+)/<a href=$1 target=_blank>$1<\/a>/g;
$mail && ($name = "<a href=\"mailto\:$mail\">$name </a>");
($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
$month = ($mon + 1);
$year %= 100;
$year < 10 && ($year = "0$year");
$month < 10 && ($month = "0$month");
$mday < 10 && ($mday = "0$mday");
$sec < 10 && ($sec = "0$sec");
$min < 10 && ($min = "0$min");
$hour < 10 && ($hour = "0$hour");
$wday = ("日", "月", "火", "水", "木", "金", "土")[$wday];
$date = "$month月$mday日($wday)$hour時$min分$sec秒";
$res = "$year$month$mday$hour$min$sec" unless $res;

$file = "./$folder/$res.html";
open(W, "+< $file") || $subj && open(W, "> $file") || &error('スレッドがありません.');
flock(W, 2);
while(<W>){
	last unless /<dt>(\d+)/;
	$cnt = $1;
	$pos = tell(W);
	$prev = $_;
}
seek(W, $pos, 0);
$cnt++;

$prev =~ /<b>(.+) <\/b>.+<dd>(.+) <\/dl>/;
$name eq $1 && $comm eq $2 && print W && &error('二重カキコです.');
if($subj){
	$subj1 = "<title>$subj </title>";
	$subj2 = "<font size=+2 color=red><b>$subj </b></font>";
}
$line = <<EOL;
$subj1<dl><dt>$cnt$subj2投稿者：<font color=forestgreen><b>$name </b></font>
<font size=-1>　投稿日：$date</font><br><dd>$comm </dl>
EOL
$line =~ s/\n//g;
print W "$line\n";
$line = <<EOL;
<form method=post action="../$cgi">
<input type=hidden name="res" value="$res">
投稿者 <input type=text name="name" size=20>
メール <input type=text name="mail" size=20><br>
<input type=submit value="↑へのレスカキコ" ><br>
<textarea name="comm" rows=4 cols=70 ></textarea>
</form>
EOL
$line =~ s/\n//g;
print W "$line\n";
flock(W, 8);
close(W);

}

open(R, "./blist.txt");
while(<R>){
	chop;
	($fol, $color, $title) = split(/,/);
	last if $fol eq $folder;
}
close(R);

$page = '2' if $next != 21;
$index = "index$page.html";
$file = "./$folder/$index";
$main = "(メイン)" if $folder eq 'main';
($color, $bg) = split(/!/, $color);
$bg = " background=\"$bg\"" if $bg;
$text = q( text="#ffffff" link="firebrick" vlink="firebrick") if $color =~ "#0";
$title =~ s/#c#/,/g;
$title0 = $title;
if($title0 =~ /alt=\"([^\"]+)/){
	$title0 = $1;
	undef $amezo;
}

open(W, "+< $file");
&redirect unless flock(W, 6);

print W <<EOF;
<html><head><title>$title0$amezo$main</title></head>
$copyright
<body$bg bgcolor="$color"$text>
<font size=+2>$title$amezo$main</font>
EOF

open(R, "./header.html");
print W while <R>;
close(R);

print W <<EOF;
<form method=post action="../$cgi">
<input type=submit value="次のページ">
<input type=text name="next" value="$next" size="3">～</form>
<font size=2>
<!-- HEAD LINE -->
EOF

opendir(DIR, "./$folder");
@dir = readdir(DIR);
closedir(DIR);

for($i=0;$dir[$i];$i++){
	$ts = ($dir[$i] =~ /^\d+\.html/) ?
		(stat("./$folder/$dir[$i]"))[9] - 800000000 : ' ';
	$dir[$i] = "$ts,$dir[$i]";
}
@dir = sort {$b cmp $a;} @dir;

for($i=$next - 21;$i < $next+100-21 && $dir[$i];$i++){
	($ts, $file) = split(/,/, $dir[$i]);
	last if $ts eq ' ';
	open(R, "./$folder/$file");
	$_ = <R>;
	close(R);
	/<b>([^\<]*)<\/b>/;
	$j = $i+1;
	print W " $j<a href=\"$file\">$1</a>\n";
}
print W "<!-- HEAD LINE END -->\n</font>\n";

for($i=$next - 21;$i < $next - 1 && $dir[$i];$i++){
	($ts, $file) = split(/,/, $dir[$i]);
	last if $ts eq ' ';
	print W <<EOL;
<table border=1 cellspacing=1 cellpadding=2 width=100% bgcolor="#efefef"><tr><td><font color="#000000">
EOL
	open(R, "./$folder/$file");
	$_ = <R>;
	s/<title>.*<\/title>//;
	print W;
	for($j=0;<R>;$j++){
		last if /^<form/; 
		$lines[$j % 7] = $_;
	}
	close(R);
	$k = $j - 7;
	$k = 0 if $k < 0;
	for($m=$k;$m < $j;$m++){
		print W "$lines[$m % 7]";
	}
	$file =~ /(.+)\.html/;
	$res = $1;
	undef $sub;
	$k = $j - 98;
	$sub = <<EOL if $j > 200;
<input type=text name="from" value="$k" size="4">
<input type=submit name="sub" value="～">　
EOL
	print W <<EOL;
</font></td></tr></table>
<form method=post action="../$cgi">
<input type=hidden name="res" value="$res">
投稿者 <input type=text name="name" size=20>
メール <input type=text name="mail" size=20><br>
<input type=submit value="↑へのレスカキコ" >
<a href="$res.html">レス全部を見る</a>
$sub<a href="#top">上へ　</a><a href="./">リロード</a><br>
<textarea name="comm" rows=4 cols=70 ></textarea>
</form><hr>
</td></tr></table>
EOL

}

print W <<EOF;
<form method=post action="../$cgi">
<input type=submit value="次のページ">
<input type=text name="next" value="$next" size="3">～</form>
<hr></body></html>
EOF

truncate(W, tell(W));
flock(W, 8);
close(W);
&redirect;

sub redirect {
	undef $index unless $page;
	print "Location: $urlbase$folder/$index\n\n\n";
	exit;
}

sub error {
	print "Content-type: text/html\n\n<html><body><h2>$_[0]</h2></body></html>";
	exit;
}

sub res {
	print "Content-type: text/html\n\n";
	open(R, "./$folder/$res.html");
	print <R>."";
	while(<R>){
		/<dt>(\d+)/;
		last if $1 >= $form{'from'};
	}
	print;
	$fol = "<input type=hidden name=\"folder\" value=\"$folder\">";
	while(<R>){
		if(/<\/form>/){
			s/(action=\")\.\.\//$1/;
			s/(<\/form>)/$fol$1/;
		}
		print;
	}
	exit;
}

sub del {
	if($mail){
		$name = $admin;
		undef $mail unless $name =~ /\@/;
		return;
	}
	print "Content-type: text/html\n\n";
	exit unless $res;
	$file = "./$folder/$res.html";
	if(!$comm){
		unlink($file);
		exit;
	}
	$comm = ',' . $comm . ',';
	$comm =~ s/(\d+)\-(\d+)/join(',',($1..$2))/eg;
	$comm =~ s/<br>/,/g;
	$ts = (stat($file))[9];
	open(R, $file);
	@lines = <R>;
	close(R);
	open(W, "+> $file");
	flock(W, 2);
	foreach(@lines){
		next if /<dt>(\d+)/ && ($n=','.$1.',') && $comm =~ /$n/;
		print W;
	}
	close(W);
	utime $ts+1, $ts+1, $file;
	exit;
}
