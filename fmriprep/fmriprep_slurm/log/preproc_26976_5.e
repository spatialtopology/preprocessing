Error for command "run": unknown flag: --participant_label

Options for run command:

      --add-caps string        a comma separated capability list to add
      --allow-setuid           allow setuid binaries in container (root only)
      --app string             set an application to run inside a container
      --apply-cgroups string   apply cgroups from file for container processes (root only)
  -B, --bind strings           a user-bind path specification.  spec has the format src[:dest[:opts]], where src and dest
                               are outside and inside paths.  If dest is not given, it is set equal to src.  Mount options
                               ('opts') may be specified as 'ro' (read-only) or 'rw' (read/write, which is the default).
                               Multiple bind paths can be given by a comma separated list.
  -e, --cleanenv               clean environment before running container
  -c, --contain                use minimal /dev and empty other directories (e.g. /tmp and $HOME) instead of sharing
                               filesystems from your host
  -C, --containall             contain not only file systems, but also PID, IPC, and environment
      --disable-cache          dont use cache, and dont create cache
      --dns string             list of DNS server separated by commas to add in resolv.conf
      --docker-login           login to a Docker Repository interactively
      --drop-caps string       a comma separated capability list to drop
      --env strings            pass environment variable to contained process
      --env-file string        pass environment variables from file to contained process
  -f, --fakeroot               run container in new user namespace as uid 0
      --fusemount strings      A FUSE filesystem mount specification of the form '<type>:<fuse command> <mountpoint>' -
                               where <type> is 'container' or 'host', specifying where the mount will be performed
                               ('container-daemon' or 'host-daemon' will run the FUSE process detached). <fuse command> is
                               the path to the FUSE executable, plus options for the mount. <mountpoint> is the location in
                               the container to which the FUSE mount will be attached. E.g. 'container:sshfs 10.0.0.1:/
                               /sshfs'. Implies --pid.
  -h, --help                   help for run
  -H, --home string            a home directory specification.  spec can either be a src path or src:dest pair.  src is the
                               source path of the home directory outside the container and dest overrides the home
                               directory within the container. (default "/dartfs-hpc/rc/home/1/f0042x1")
      --hostname string        set container hostname
  -i, --ipc                    run container in a new IPC namespace
      --keep-privs             let root user keep privileges in container (root only)
  -n, --net                    run container in a new network namespace (sets up a bridge network interface by default)
      --network string         specify desired network type separated by commas, each network will bring up a dedicated
                               interface inside container (default "bridge")
      --network-args strings   specify network arguments to pass to CNI plugins
      --no-home                do NOT mount users home directory if /home is not the current working directory
      --no-init                do NOT start shim process with --pid
      --no-mount strings       disable one or more mount xxx options set in singularity.conf
      --no-privs               drop all privileges from root user in container)
      --no-umask               do not propagate umask to the container, set default 0022 umask
      --nohttps                do NOT use HTTPS with the docker:// transport (useful for local docker registries without a
                               certificate)
      --nonet                  disable VM network handling
      --nv                     enable experimental Nvidia support
  -o, --overlay strings        use an overlayFS image for persistent data storage or as read-only layer of container
      --passphrase             prompt for an encryption passphrase
      --pem-path string        enter an path to a PEM formated RSA key for an encrypted container
  -p, --pid                    run container in a new PID namespace
      --pwd string             initial working directory for payload process inside the container
      --rocm                   enable experimental Rocm support
  -S, --scratch strings        include a scratch directory within the container that is linked to a temporary dir (use -W
                               to force location)
      --security strings       enable security features (SELinux, Apparmor, Seccomp)
  -u, --userns                 run container in a new user namespace, allowing Singularity to run completely unprivileged
                               on recent kernels. This disables some features of Singularity, for example it only works
                               with sandbox images.
      --uts                    run container in a new UTS namespace
      --vm                     enable VM support
      --vm-cpu string          number of CPU cores to allocate to Virtual Machine (implies --vm) (default "1")
      --vm-err                 enable attaching stderr from VM
      --vm-ip string           IP Address to assign for container usage. Defaults to DHCP within bridge network. (default
                               "dhcp")
      --vm-ram string          amount of RAM in MiB to allocate to Virtual Machine (implies --vm) (default "1024")
  -W, --workdir string         working directory to be used for /tmp, /var/tmp and $HOME (if -c/--contain was also used)
  -w, --writable               by default all Singularity containers are available as read only. This option makes the file
                               system accessible as read/write.
      --writable-tmpfs         makes the file system accessible as read-write with non persistent data (with overlay
                               support only)

Run 'singularity --help' for more detailed usage information.
