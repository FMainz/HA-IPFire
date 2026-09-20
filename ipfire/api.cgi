#!/usr/bin/perl
###############################################################################
#                                                                             #
# IPFireAPI for Home Assistant                                                #
#                                                                             #
# This CGI provides system, network, service, add-on, traffic, and            #
# connection information from IPFire for the HA-IPFire integration.           #
#                                                                             #
###############################################################################

use strict;
use warnings;

require '/var/ipfire/general-functions.pl';
require "/opt/pakfire/lib/functions.pl";
use JSON::PP;

my $api_version = "1";

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

sub read_file {
    my ($path) = @_;

    open(my $fh, '<', $path) or return undef;
    my $value = <$fh>;
    close($fh);

    return undef unless defined $value;
    chomp $value;

    return $value;
}

sub traffic_data {
    my $interface = read_file('/var/ipfire/red/iface');

    return (undef, undef) unless defined $interface;
    return (undef, undef) unless $interface =~ /^[A-Za-z0-9_.:-]+$/;

    my $rx_bytes = read_file("/sys/class/net/$interface/statistics/rx_bytes");
    my $tx_bytes = read_file("/sys/class/net/$interface/statistics/tx_bytes");

    return (undef, undef)
        unless defined $rx_bytes && defined $tx_bytes;

    return (undef, undef)
        unless $rx_bytes =~ /^\d+$/ && $tx_bytes =~ /^\d+$/;

    return (int($rx_bytes), int($tx_bytes));
}

sub system_data {
    open(my $fh, '<', '/etc/system-release') or return ('', 0, 0);

    my $version = <$fh>;
    close($fh);

    chomp($version) if defined $version;

    my %pakfire_status = &Pakfire::status();

    my $core_update =
        (($pakfire_status{'CoreUpdateAvailable'} // '') eq 'yes');

    my $package_updates =
        $pakfire_status{'PakUpdatesAvailable'} // 0;

    $package_updates = 0 unless $package_updates =~ /^\d+$/;
    $package_updates = int($package_updates);

    return (
        defined $version ? $version : '',
        $core_update,
        $package_updates,
    );
}

sub fireinfo_data {
    my $profile_file = '/var/ipfire/fireinfo/profile';

    open(my $fh, '<', $profile_file) or return ();

    local $/;
    my $json = <$fh>;
    close($fh);

    my $data = eval { decode_json($json) };
    return () if $@ || !ref($data);

    my $profile = $data->{'profile'} // {};

    my $cpu = $profile->{'cpu'} // {};
    my $network = $profile->{'network'} // {};
    my $system = $profile->{'system'} // {};

    return (
        $cpu->{'arch'} // '',
        $cpu->{'model_string'} // '',
        int($cpu->{'count'} // 0),

        $system->{'model'} // '',
        $system->{'vendor'} // '',
        int($system->{'memory'} // 0),
        int($system->{'root_size'} // 0),
        $system->{'virtual'} ? 1 : 0,

        $network->{'blue'} ? 1 : 0,
        $network->{'green'} ? 1 : 0,
        $network->{'orange'} ? 1 : 0,
        $network->{'red'} ? 1 : 0,
    );
}

sub services_data {
    my %services = (
        'dhcp' => {
            'process' => 'dhcpd',
        },
        'web_server' => {
            'process' => 'httpd',
        },
        'cron' => {
            'process' => 'fcron',
        },
        'dns_resolver' => {
            'process' => 'kresd',
        },
        'logging' => {
            'process' => 'syslogd',
        },
        'ntp' => {
            'process' => 'ntpd',
        },
        'ssh' => {
            'process' => 'sshd',
        },
        'vpn' => {
            'process' => 'charon',
        },
        'web_proxy' => {
            'process' => 'squid',
        },
        'ips' => {
            'pidfile' => '/var/run/suricata.pid',
        },
        'ovpn_roadwarrior' => {
            'process' => 'openvpn',
            'pidfile' => '/var/run/openvpn-rw.pid',
        },
        'lldp' => {
            'process' => 'lldpd',
        },
        'dbus' => {
            'process' => 'dbus-daemon',
            'pidfile' => '/var/run/dbus/pid',
        },
    );

    my %status;

    foreach my $service (keys %services) {
        my %config = %{ $services{$service} };

        my @pids;

        if (defined $config{'pidfile'}) {
            @pids = &General::read_pids($config{'pidfile'});
        } else {
            @pids = &General::find_pids($config{'process'});
        }

        $status{$service} = scalar(@pids) ? 1 : 0;
    }

    return %status;
}

sub addons_data {
    my %addons;

    my %paklist = &Pakfire::dblist("installed");

    foreach my $pak (sort keys %paklist) {
        my %metadata = &Pakfire::getmetadata($pak, "installed");

        next unless "$metadata{'Services'}";

        foreach my $service (split(/ /, "$metadata{'Services'}")) {
            next unless $service;

            my @status = &General::system_output(
                "/usr/local/bin/addonctrl",
                "$pak",
                "status",
                "$service"
            );

            my $output = join('', @status);

            my $running =
                ($output =~ /is\ running/ && $output !~ /is\ not\ running/);

            $addons{$pak} = {
                'running' => $running ? 1 : 0,
            };
        }
    }

    return %addons;
}

my ($version, $core_update, $package_updates) = system_data();
my ($rx_bytes, $tx_bytes) = traffic_data();

my (
    $architecture,
    $cpu_model,
    $cpu_count,
    $model,
    $vendor,
    $memory,
    $root_size,
    $virtual,
    $blue,
    $green,
    $orange,
    $red,
) = fireinfo_data();

my $pakfire_version = &Pakfire::make_version();
my @kernel_version = &General::system_output("uname", "-r");
my $kernel_release = $kernel_version[0] // '';
chomp($kernel_release);

my %services = services_data();
my %addons = addons_data();

# -----------------------------------------------------------------------------
# HTTP response
# -----------------------------------------------------------------------------

print "Content-Type: application/json; charset=utf-8\r\n";
print "Cache-Control: no-store, no-cache, must-revalidate\r\n";
print "Pragma: no-cache\r\n";
print "\r\n";

# The API provides read-only system data and connection control.
my $method = $ENV{'REQUEST_METHOD'} // 'GET';

# -----------------------------------------------------------------------------
# Connection control
# -----------------------------------------------------------------------------
#
# Connection actions are only accepted from the HA-IPFire integration.
# The IPFire WebGUI already protects this CGI with HTTP authentication.
#
# HA-IPFire sends:
#   X-HA-IPFire-API: 1
#
# and a form-encoded POST body:
#   action=connect
#   action=disconnect
#
if ($method eq 'POST') {
    my $api_header = $ENV{'HTTP_X_HA_IPFIRE_API'} // '';

    if ($api_header ne '1') {
        print '{"api_version":'.$api_version.',"error":"forbidden"}';
        exit 0;
    }

    my $content_length = $ENV{'CONTENT_LENGTH'} // 0;
    my $body = '';

    if ($content_length =~ /^\d+$/ && $content_length > 0) {
        read(STDIN, $body, $content_length);
    }

    my $action = '';
    if ($body =~ /(?:^|&)action=([^&]*)/) {
        $action = $1;
        $action =~ tr/+/ /;
        $action =~ s/%([0-9A-Fa-f]{2})/chr(hex($1))/eg;
    }

    if ($action ne 'connect' && $action ne 'disconnect') {
        print '{"api_version":'.$api_version.',"error":"invalid_action"}';
        exit 0;
    }

    my $redctrl = '/usr/local/bin/redctrl';

    unless (-x $redctrl) {
        print '{"api_version":'.$api_version.',"error":"redctrl_not_found"}';
        exit 0;
    }

    my $command;

    if ($action eq 'connect') {
        $command = -e "${General::swroot}/red/active"
            ? 'restart'
            : 'start';
    } elsif ($action eq 'disconnect') {
        if (!-e "${General::swroot}/red/active") {
            print '{"api_version":'.$api_version.',"result":"ok"}';
            exit 0;
        }

        $command = 'stop';
    }
    unless (defined $command) {
        print '{"api_version":'.$api_version.',"result":"error","error":"invalid_action"}';
        exit 0;
    }

    my $result;

    {
        open my $null, '>', '/dev/null'
            or die "Cannot open /dev/null: $!";

        local *STDOUT = $null;
        local *STDERR = $null;

        $result = system("$redctrl $command >/dev/null 2>&1");
    }

    if ($result == 0) {
        print '{"api_version":'.$api_version.',"result":"ok"}';
    } else {
        my $exit_code = $result >> 8;
        print '{"api_version":'.$api_version.',"result":"error","error":"redctrl_failed","exit_code":'
            . $exit_code
            . "}";
    }

    exit 0;
}

if ($method ne 'GET') {
    print '{"api_version":'.$api_version.',"error":"method_not_allowed"}';
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

my $external_ip = read_file("${General::swroot}/red/local-ipaddress");
my $external_hostname = '';

if ($external_ip ne '') {
    $external_hostname =
        (gethostbyaddr(pack("C4", split(/\./, $external_ip)), 2))[0]
        || '';
}

# -----------------------------------------------------------------------------
# JSON response
# -----------------------------------------------------------------------------

my @json;
push @json, '"api_version":'.$api_version;

push @json, '"system":{'
    . '"version":' . json_string($version)
    . ',"pakfire_version":' . json_string($pakfire_version)
    . ',"kernel_version":' . json_string($kernel_release)
    . ',"architecture":' . json_string($architecture)
    . ',"cpu_model":' . json_string($cpu_model)
    . ',"cpu_count":' . $cpu_count
    . ',"model":' . json_string($model)
    . ',"vendor":' . json_string($vendor)
    . ',"memory":' . $memory
    . ',"root_size":' . $root_size
    . ',"virtual":' . ($virtual ? 'true' : 'false')
    . ',"core_update":' . ($core_update ? 'true' : 'false')
    . ',"package_updates":' . $package_updates
    . '}';

push @json, '"network":{'
    . '"blue":' . ($blue ? 'true' : 'false')
    . ',"green":' . ($green ? 'true' : 'false')
    . ',"orange":' . ($orange ? 'true' : 'false')
    . ',"red":' . ($red ? 'true' : 'false')
    . '}';

push @json, '"services":{'
    . '"dhcp":' . ($services{'dhcp'} ? 'true' : 'false')
    . ',"web_server":' . ($services{'web_server'} ? 'true' : 'false')
    . ',"cron":' . ($services{'cron'} ? 'true' : 'false')
    . ',"dns_resolver":' . ($services{'dns_resolver'} ? 'true' : 'false')
    . ',"logging":' . ($services{'logging'} ? 'true' : 'false')
    . ',"ntp":' . ($services{'ntp'} ? 'true' : 'false')
    . ',"ssh":' . ($services{'ssh'} ? 'true' : 'false')
    . ',"vpn":' . ($services{'vpn'} ? 'true' : 'false')
    . ',"web_proxy":' . ($services{'web_proxy'} ? 'true' : 'false')
    . ',"ips":' . ($services{'ips'} ? 'true' : 'false')
    . ',"ovpn_roadwarrior":' . ($services{'ovpn_roadwarrior'} ? 'true' : 'false')
    . ',"lldp":' . ($services{'lldp'} ? 'true' : 'false')
    . ',"dbus":' . ($services{'dbus'} ? 'true' : 'false')
    . '}';

my @addon_json;

foreach my $addon (sort keys %addons) {
    push @addon_json,
        json_string($addon)
        . ':{'
        . '"running":' . ($addons{$addon}{'running'} ? 'true' : 'false')
        . '}';
}

push @json, '"addons":{' . join(',', @addon_json) . '}';

push @json, '"traffic":{'
    . '"rx_bytes":' . (defined $rx_bytes ? $rx_bytes : 'null')
    . ',"tx_bytes":' . (defined $tx_bytes ? $tx_bytes : 'null')
    . '}';

my @connection;
push @connection, '"state":' . json_string($state);

if (defined $connected_since) {
    push @connection, '"connected_since":' . $connected_since;
    push @connection, '"duration":' . int($duration);
    push @connection, '"duration_text":' . json_string(&General::format_time(int($duration)));
} else {
    push @connection, '"connected_since":null';
    push @connection, '"duration":0';
    push @connection, '"duration_text":""';
}

push @connection, '"profile":' . json_string($profile);
push @connection, '"external_ip":' . json_string($external_ip);
push @connection, '"external_hostname":' . json_string($external_hostname);

push @json, '"connection":{' . join(',', @connection) . '}';

print '{' . join(',', @json) . "}\n";

exit 0;
