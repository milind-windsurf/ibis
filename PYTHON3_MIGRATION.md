# Python 3 Migration Guide for IBIS

## Overview

This document provides comprehensive information about the Python 3 migration for the IBIS project. The migration is being conducted in multiple phases to ensure stability and minimize disruption.

## Migration Status

### ✅ Phase 1: Environment and Build System Updates (COMPLETED)

**Objective**: Update environment setup, build scripts, and packaging to support Python 3.6+ instead of Python 2.7.8.

**Changes Made**:

#### 1. Python Version Validation (`setup.sh`)
- **Before**: Required Python 2.7.x exactly
- **After**: Requires Python 3.6+ minimum
- **Impact**: Setup script now validates for modern Python 3 versions

```bash
# Old validation logic
supported_major_ver="2"
if [ $minor_ver -lt 7 ]; then
    unsupported_version=true
fi

# New validation logic  
supported_major_ver="3"
if [ $minor_ver -lt 6 ]; then
    unsupported_version=true
fi
```

#### 2. System Dependencies (`setup.sh`)
- **Before**: `python-devel`, `python-setuptools`
- **After**: `python3-devel`, `python3-setuptools`
- **Impact**: Ensures correct development headers and tools for Python 3

#### 3. Build System (`ibis_build/build.sh`)
- **Before**: `python2.7 $ibis_home/setup.py bdist_egg`
- **After**: `python3 $ibis_home/setup.py bdist_egg`
- **Impact**: Egg files are now built with Python 3

#### 4. Egg Naming Convention
- **Before**: `py2.7.egg` format
- **After**: `py3.x.egg` format
- **Files Updated**: `ibis-shell`, `ibis_version.sh`
- **Impact**: Runtime scripts now look for Python 3 egg files

#### 5. Python 3 Compatibility (`setup.py`)
- **Before**: Used deprecated `pip.req` import
- **After**: Removed incompatible import
- **Impact**: Setup script is now Python 3 compatible

#### 6. Documentation Updates
- Updated all references from Python 2.7.8 to Python 3.x
- Updated installation instructions with correct package names
- Files: `docs/setup_ibis.md`, `docs/help.md`

## Installation Requirements (Updated)

### System Requirements
- **Operating System**: Unix-like environment (Linux, Mac, AIX)
- **Python Version**: Python 3.6+ (previously Python 2.7.8)
- **Hadoop Ecosystem**: Oozie, Hive/Impala, Sqoop

### System Dependencies (RHEL/CentOS)
```bash
# Development tools
sudo yum groupinstall -y "development tools"

# Python 3 and dependencies
sudo yum install -y \
    krb5-devel gcc zlib-devel gcc-c++ \
    python3-devel \
    python3-setuptools python3-setuptools-devel \
    cyrus-sasl-devel openssl openssl-devel \
    libffi-devel bzip2-devel ncurses-devel \
    sqlite-devel readline-devel tk-devel \
    gdbm-devel db4-devel libpcap-devel \
    xz-devel snappy-devel expat-devel patch \
    unzip sudo vim wget which tar gzip \
    graphviz shadow-utils git net-tools \
    libXtst.x86_64
```

## Setup Instructions (Updated)

### 1. Environment Setup
```bash
# Run the updated setup script
sh setup.sh

# The script will now:
# - Validate Python 3.6+ is installed
# - Install Python 3 development packages
# - Create required directories
# - Set up database tables
```

### 2. Build Process
```bash
# Navigate to build directory
cd ibis_build

# Build with Python 3
sh build.sh <ibis_home_path> [options]

# This will now:
# - Use python3 command for egg building
# - Generate py3.x.egg files
# - Create ibis.tar.gz with Python 3 artifacts
```

### 3. Runtime
```bash
# The ibis-shell script now expects Python 3 egg files
./ibis-shell [options]

# Egg file naming: opensource_ibis-0.9.2-BETA-py3.x.egg
```

## Testing Your Migration

### 1. Verify Python Version Detection
```bash
# Test the validation function
cd /path/to/ibis
source setup.sh
validate_python_version
```

### 2. Test Build Process
```bash
# Full build test
cd ibis_build
sh build.sh /path/to/ibis

# Verify egg file creation
ls -la dist/*.egg
# Should see: opensource_ibis-*-py3.x.egg
```

### 3. Test Runtime
```bash
# Test shell execution
./ibis-shell --help
```

## Potential Issues and Solutions

### Issue 1: Python 3 Command Not Found
**Problem**: `python3` command not available
**Solution**: 
```bash
# Install Python 3 or create symlink
sudo yum install python3
# OR
sudo ln -s /usr/bin/python3.x /usr/bin/python3
```

### Issue 2: Missing Python 3 Development Headers
**Problem**: Build fails with missing Python.h
**Solution**:
```bash
sudo yum install python3-devel
```

### Issue 3: Egg File Not Found
**Problem**: Runtime can't find py3.x.egg file
**Solution**: Verify build completed successfully and egg file exists in expected location

## Future Migration Phases

### 🔄 Phase 2: Python Syntax Updates (PLANNED)
- Update print statements: `print "text"` → `print("text")`
- Update import statements for Python 3 compatibility
- Update string/Unicode handling
- Update exception handling syntax

### 🔄 Phase 3: Dependency Updates (PLANNED)
- Update requirements.pip for Python 3 compatible versions
- Test and update third-party library compatibility
- Update any deprecated library usage

### 🔄 Phase 4: Testing and Validation (PLANNED)
- Update test suite for Python 3
- Comprehensive integration testing
- Performance validation

## Rollback Instructions

If you need to rollback to Python 2.7:

1. **Revert system packages**:
   ```bash
   sudo yum install python-devel python-setuptools python-setuptools-devel
   ```

2. **Revert code changes**: Use git to revert to the commit before the migration
   ```bash
   git revert <migration_commit_hash>
   ```

3. **Update configuration**: Ensure all scripts point back to Python 2.7

## Support and Troubleshooting

### Common Commands for Debugging
```bash
# Check Python version
python3 --version

# Check installed packages
pip3 list

# Verify egg file contents
python3 -m zipfile -l path/to/file.egg

# Test import capabilities
python3 -c "import ibis"
```

### Getting Help
- Review the original setup documentation in `docs/setup_ibis.md`
- Check the help documentation in `docs/help.md`
- Examine the build logs in `ibis_build/` directory

## Migration Checklist

- [ ] Python 3.6+ installed and accessible via `python3` command
- [ ] All system dependencies updated to Python 3 versions
- [ ] Setup script runs without errors
- [ ] Build process completes successfully
- [ ] Egg files generated with py3.x naming
- [ ] Runtime scripts execute without import errors
- [ ] All team members updated on new requirements

---

**Migration completed**: Phase 1 - Environment and Build System Updates  
**Next phase**: Python Syntax Updates  
**Documentation updated**: August 2025
