/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/.
 *
 * This file is part of zmqpp.
 * Copyright (c) 2011-2015 Contributors as noted in the AUTHORS file.
 */

#include <zmqpp/zmqpp.hpp>
#include <string>
#include <iostream>

using namespace std;

int main(int argc, char *argv[]) {
  const string endpoint = "tcp://*:4242";

  // initialize the 0MQ context
  zmqpp::context context;

}