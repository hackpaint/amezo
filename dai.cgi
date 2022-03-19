#!/usr/bin/perl

$copyright = <<EOL;
<!-- 
     Script for amezo-like BBS HEAD LINE
     Copyright (C) 2000 amezo_
     http://www17.big.or.jp/~amezo_/
-->
EOL

if($ENV{'QUERY_STRING'}){
	print "Content-type: text/plain\n\n";
	open(R, "./dai.cgi");
	print while <R>;
	close(R);
	exit;
}

print "Content-type: text/html\n\n";

open(B, "./blist.txt");
while(<B>){
	chop;
	($folder, $color, $title) = split(/,/);
	$color =~ s/!.*//;
	next if $folder =~ /^\./;
	print <<EOF;
<table border=0 cellspacing=1 cellpadding=2 width=100% bgcolor="$color"><tr><td>
<a href="$folder/" target="naka"><b><font size="3" color="F92500">$title</a></font></b> 
EOF
	open(R, "./$folder/index.html");
	while(<R>){
		last if /<!-- HEAD LINE -->/;
	}
	for($i=0;$i<20 && ($_ = <R>);$i++){
		last if /<!-- HEAD LINE END -->/;
		s/(\d+\.html)/$folder\/$1/;
		print;
	}
	close(R);
	print "</td></tr></table>\n";
}
close(B);
