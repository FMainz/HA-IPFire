#!/usr/bin/perl
###############################################################################
#                                                                             #
# HA-IPFire - Home Assistant API for IPFire                                 #
#                                                                             #
# This CGI is intended to be installed manually on an IPFire system during   #
# development of HA-IPFire v0.3.0.                                           #
#                                                                             #
# It currently provides read-only connection information.                     #
# Connect/disconnect actions will be added only after the read-only API has  #
# been tested successfully.                                                  #
#                                                                             #
###############################################################################

use strict;
use warnings;

require '/var/ipfire/general-functions.pl';

# -----------------------------------------------------------------------------
# JSON helper
# -----------------------------------------------------------------------------

sub json_escape {
    my ($value) = @_;

    $value //= '';
    $value =~ s/\\/\\\\/g;
    $value =~ s/"/\\"/g;
    $value =~ s/\r/\\r/g;
    $value =~ s/\n/\\n/g;
    $value =~ s/\t/\\t/g;

    return $value;
}

sub json_string {
    my ($value) = @_;
    return '"' . json_escape($value) . '"';
}

# -----------------------------------------------------------------------------
# HTTP response
# -----------------------------------------------------------------------------

print "Content-Type: application/json; charset=utf-8\r\n";
print "Cache-Control: no-store, no-cache, must-revalidate\r\n";
print "Pragma: no-cache\r\n";
print "\r\n";

# The first version is deliberately read-only.
my $method = $ENV{'REQUEST_METHOD'} // 'GET';

if ($method ne 'GET') {
    print '{"api_version":1,"error":"method_not_allowed"}\n';
    exit 0;
}

# -----------------------------------------------------------------------------
# Read IPFire connection information
# -----------------------------------------------------------------------------

my %pppsettings = ();
&General::readhash("${General::swroot}/ppp/settings", \%pppsettings);

my $state = 'disconnected';
my $duration = 0;
my $connected_since = undef;

# IPFire creates /var/ipfire/red/active while the RED connection is active.
# Its modification time is also used by Header::connectionstatus() to display
# the connection age.
my $active_file = "${General::swroot}/red/active";

if (-e $active_file) {
    my @stat = stat($active_file);
    my $mtime = $stat[9];

    if (defined $mtime) {
        $connected_since = int($mtime);
        $duration = time() - $mtime;
        $duration = 0 if $duration < 0;
    }

    $state = 'connected';
} else {
    # Match IPFire's own connectionstatus() logic:
    # keepconnected + running pppd means that the connection is being brought
    # up; otherwise the connection is closed.
    my $keepconnected = "${General::swroot}/red/keepconnected";

    if (-e $keepconnected) {
        my $pppd_running = system("ps -ef | grep -q '[p]ppd'") == 0;
        $state = 'connecting' if $pppd_running;
    }
}

my $profile = $pppsettings{'PROFILENAME'} // '';

# -----------------------------------------------------------------------------
# JSON response
# -----------------------------------------------------------------------------

my @json;
push @json, '"api_version":1';
push @json, '"connection":{';
push @json, '"state":' . json_string($state);

if (defined $connected_since) {
    push @json, '"connected_since":' . $connected_since;
    push @json, '"duration":' . int($duration);
    push @json, '"duration_text":' . json_string(&General::format_time(int($duration)));
} else {
    push @json, '"connected_since":null';
    push @json, '"duration":0';
    push @json, '"duration_text":""';
}

push @json, '"profile":' . json_string($profile);
push @json, '}';

print '{' . join(',', @json) . "}\n";

exit 0;
