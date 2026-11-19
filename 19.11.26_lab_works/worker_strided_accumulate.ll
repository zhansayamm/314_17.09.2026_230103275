define range(i32 0, 2) i32 @_ZN8__main__25worker_strided_accumulateB2v1B40c8tJTIeFIjxB2IKSgI4CrvQClQZ6FcpCShpgEU0AE5ArrayIyLi1E1C7mutable7alignedExxy(ptr noalias writeonly captures(none) %retptr, ptr noalias writeonly captures(none) %excinfo, ptr readnone captures(none) %arg.buffer.0, ptr readnone captures(none) %arg.buffer.1, i64 %arg.buffer.2, i64 %arg.buffer.3, ptr captures(none) %arg.buffer.4, i64 %arg.buffer.5.0, i64 %arg.buffer.6.0, i64 %arg.slot, i64 %arg.iters, i64 %arg.seed) local_unnamed_addr #0 {
B0:
  %.23 = or i64 %arg.seed, 1
  %.42 = icmp eq i64 %arg.buffer.5.0, 0
  br i1 %.42, label %B0.if, label %B0.else.if, !prof !0

B122:                                             ; preds = %B122.preheader, %B423.7
  %lsr.iv = phi i64 [ %3, %B122.preheader ], [ %lsr.iv.next, %B423.7 ]
  %x.4.0114 = phi i64 [ %.213.7, %B423.7 ], [ %x.4.0114.unr, %B122.preheader ]
  %.205 = shl i64 %x.4.0114, 13
  %.207 = xor i64 %.205, %x.4.0114
  %.210 = lshr i64 %.207, 7
  %.211 = xor i64 %.210, %.207
  %.212 = shl i64 %.211, 17
  %.213 = xor i64 %.212, %.211
  %sunkaddr = mul i64 %.232, 8
  %sunkaddr3 = getelementptr inbounds i8, ptr %0, i64 %sunkaddr
  %.247 = load i64, ptr %sunkaddr3, align 8
  %.249 = lshr i64 %.213, 40
  %.250 = add i64 %.249, %.247
  store i64 %.250, ptr %sunkaddr3, align 8
  %.282 = icmp eq i64 %.250, -1
  br i1 %.282, label %B410, label %B423

B410:                                             ; preds = %B122
  %sunkaddr4 = mul i64 %.301, 8
  %sunkaddr5 = getelementptr inbounds i8, ptr %1, i64 %sunkaddr4
  store i64 %.213, ptr %sunkaddr5, align 8
  br label %B423

common.ret:                                       ; preds = %B0.if, %B422
  %common.ret.op = phi i32 [ 0, %B422 ], [ 1, %B0.if ]
  ret i32 %common.ret.op

B422:                                             ; preds = %B423.7, %B122.prol.loopexit, %B0.else.if
  store ptr null, ptr %retptr, align 8
  br label %common.ret

B423:                                             ; preds = %B122, %B410
  %.205.1 = shl i64 %.213, 13
  %.207.1 = xor i64 %.205.1, %.213
  %.210.1 = lshr i64 %.207.1, 7
  %.211.1 = xor i64 %.210.1, %.207.1
  %.212.1 = shl i64 %.211.1, 17
  %.213.1 = xor i64 %.212.1, %.211.1
  %sunkaddr6 = mul i64 %.232, 8
  %sunkaddr7 = getelementptr i8, ptr %0, i64 %sunkaddr6
  %.247.1 = load i64, ptr %sunkaddr7, align 8
  %.249.1 = lshr i64 %.213.1, 40
  %.250.1 = add i64 %.249.1, %.247.1
  store i64 %.250.1, ptr %sunkaddr7, align 8
  %.282.1 = icmp eq i64 %.250.1, -1
  br i1 %.282.1, label %B410.1, label %B423.1

B410.1:                                           ; preds = %B423
  %sunkaddr8 = mul i64 %.301, 8
  %sunkaddr9 = getelementptr i8, ptr %1, i64 %sunkaddr8
  store i64 %.213.1, ptr %sunkaddr9, align 8
  br label %B423.1

B423.1:                                           ; preds = %B410.1, %B423
  %.205.2 = shl i64 %.213.1, 13
  %.207.2 = xor i64 %.205.2, %.213.1
  %.210.2 = lshr i64 %.207.2, 7
  %.211.2 = xor i64 %.210.2, %.207.2
  %.212.2 = shl i64 %.211.2, 17
  %.213.2 = xor i64 %.212.2, %.211.2
  %sunkaddr10 = mul i64 %.232, 8
  %sunkaddr11 = getelementptr i8, ptr %0, i64 %sunkaddr10
  %.247.2 = load i64, ptr %sunkaddr11, align 8
  %.249.2 = lshr i64 %.213.2, 40
  %.250.2 = add i64 %.249.2, %.247.2
  store i64 %.250.2, ptr %sunkaddr11, align 8
  %.282.2 = icmp eq i64 %.250.2, -1
  br i1 %.282.2, label %B410.2, label %B423.2

B410.2:                                           ; preds = %B423.1
  %sunkaddr12 = mul i64 %.301, 8
  %sunkaddr13 = getelementptr i8, ptr %1, i64 %sunkaddr12
  store i64 %.213.2, ptr %sunkaddr13, align 8
  br label %B423.2

B423.2:                                           ; preds = %B410.2, %B423.1
  %.205.3 = shl i64 %.213.2, 13
  %.207.3 = xor i64 %.205.3, %.213.2
  %.210.3 = lshr i64 %.207.3, 7
  %.211.3 = xor i64 %.210.3, %.207.3
  %.212.3 = shl i64 %.211.3, 17
  %.213.3 = xor i64 %.212.3, %.211.3
  %sunkaddr14 = mul i64 %.232, 8
  %sunkaddr15 = getelementptr i8, ptr %0, i64 %sunkaddr14
  %.247.3 = load i64, ptr %sunkaddr15, align 8
  %.249.3 = lshr i64 %.213.3, 40
  %.250.3 = add i64 %.249.3, %.247.3
  store i64 %.250.3, ptr %sunkaddr15, align 8
  %.282.3 = icmp eq i64 %.250.3, -1
  br i1 %.282.3, label %B410.3, label %B423.3

B410.3:                                           ; preds = %B423.2
  %sunkaddr16 = mul i64 %.301, 8
  %sunkaddr17 = getelementptr i8, ptr %1, i64 %sunkaddr16
  store i64 %.213.3, ptr %sunkaddr17, align 8
  br label %B423.3

B423.3:                                           ; preds = %B410.3, %B423.2
  %.205.4 = shl i64 %.213.3, 13
  %.207.4 = xor i64 %.205.4, %.213.3
  %.210.4 = lshr i64 %.207.4, 7
  %.211.4 = xor i64 %.210.4, %.207.4
  %.212.4 = shl i64 %.211.4, 17
  %.213.4 = xor i64 %.212.4, %.211.4
  %sunkaddr18 = mul i64 %.232, 8
  %sunkaddr19 = getelementptr i8, ptr %0, i64 %sunkaddr18
  %.247.4 = load i64, ptr %sunkaddr19, align 8
  %.249.4 = lshr i64 %.213.4, 40
  %.250.4 = add i64 %.249.4, %.247.4
  store i64 %.250.4, ptr %sunkaddr19, align 8
  %.282.4 = icmp eq i64 %.250.4, -1
  br i1 %.282.4, label %B410.4, label %B423.4

B410.4:                                           ; preds = %B423.3
  %sunkaddr20 = mul i64 %.301, 8
  %sunkaddr21 = getelementptr i8, ptr %1, i64 %sunkaddr20
  store i64 %.213.4, ptr %sunkaddr21, align 8
  br label %B423.4

B423.4:                                           ; preds = %B410.4, %B423.3
  %.205.5 = shl i64 %.213.4, 13
  %.207.5 = xor i64 %.205.5, %.213.4
  %.210.5 = lshr i64 %.207.5, 7
  %.211.5 = xor i64 %.210.5, %.207.5
  %.212.5 = shl i64 %.211.5, 17
  %.213.5 = xor i64 %.212.5, %.211.5
  %sunkaddr22 = mul i64 %.232, 8
  %sunkaddr23 = getelementptr i8, ptr %0, i64 %sunkaddr22
  %.247.5 = load i64, ptr %sunkaddr23, align 8
  %.249.5 = lshr i64 %.213.5, 40
  %.250.5 = add i64 %.249.5, %.247.5
  store i64 %.250.5, ptr %sunkaddr23, align 8
  %.282.5 = icmp eq i64 %.250.5, -1
  br i1 %.282.5, label %B410.5, label %B423.5

B410.5:                                           ; preds = %B423.4
  %sunkaddr24 = mul i64 %.301, 8
  %sunkaddr25 = getelementptr i8, ptr %1, i64 %sunkaddr24
  store i64 %.213.5, ptr %sunkaddr25, align 8
  br label %B423.5

B423.5:                                           ; preds = %B410.5, %B423.4
  %.205.6 = shl i64 %.213.5, 13
  %.207.6 = xor i64 %.205.6, %.213.5
  %.210.6 = lshr i64 %.207.6, 7
  %.211.6 = xor i64 %.210.6, %.207.6
  %.212.6 = shl i64 %.211.6, 17
  %.213.6 = xor i64 %.212.6, %.211.6
  %sunkaddr26 = mul i64 %.232, 8
  %sunkaddr27 = getelementptr i8, ptr %0, i64 %sunkaddr26
  %.247.6 = load i64, ptr %sunkaddr27, align 8
  %.249.6 = lshr i64 %.213.6, 40
  %.250.6 = add i64 %.249.6, %.247.6
  store i64 %.250.6, ptr %sunkaddr27, align 8
  %.282.6 = icmp eq i64 %.250.6, -1
  br i1 %.282.6, label %B410.6, label %B423.6

B410.6:                                           ; preds = %B423.5
  %sunkaddr28 = mul i64 %.301, 8
  %sunkaddr29 = getelementptr i8, ptr %1, i64 %sunkaddr28
  store i64 %.213.6, ptr %sunkaddr29, align 8
  br label %B423.6

B423.6:                                           ; preds = %B410.6, %B423.5
  %.205.7 = shl i64 %.213.6, 13
  %.207.7 = xor i64 %.205.7, %.213.6
  %.210.7 = lshr i64 %.207.7, 7
  %.211.7 = xor i64 %.210.7, %.207.7
  %.212.7 = shl i64 %.211.7, 17
  %.213.7 = xor i64 %.212.7, %.211.7
  %sunkaddr30 = mul i64 %.232, 8
  %sunkaddr31 = getelementptr i8, ptr %0, i64 %sunkaddr30
  %.247.7 = load i64, ptr %sunkaddr31, align 8
  %.249.7 = lshr i64 %.213.7, 40
  %.250.7 = add i64 %.249.7, %.247.7
  store i64 %.250.7, ptr %sunkaddr31, align 8
  %.282.7 = icmp eq i64 %.250.7, -1
  br i1 %.282.7, label %B410.7, label %B423.7

B410.7:                                           ; preds = %B423.6
  %sunkaddr32 = mul i64 %.301, 8
  %sunkaddr33 = getelementptr i8, ptr %1, i64 %sunkaddr32
  store i64 %.213.7, ptr %sunkaddr33, align 8
  br label %B423.7

B423.7:                                           ; preds = %B410.7, %B423.6
  %lsr.iv.next = add i64 %lsr.iv, -8
  %.166.7 = icmp sgt i64 %lsr.iv.next, 8
  br i1 %.166.7, label %B122, label %B422

B0.if:                                            ; preds = %B0
  store ptr @.const.picklebuf.ffb24196e71d4d5274d7295bceca009ea25a5f9d, ptr %excinfo, align 8, !numba_exception_output !1
  br label %common.ret

B0.else.if:                                       ; preds = %B0
  %.166111.not = icmp slt i64 %arg.iters, 1
  br i1 %.166111.not, label %B422, label %B122.lr.ph

B122.lr.ph:                                       ; preds = %B0.else.if
  %.28 = add nsw i64 %arg.slot, 1
  %.63 = srem i64 %.28, %arg.buffer.5.0
  %.66 = icmp ne i64 %.63, 0
  %.64 = xor i64 %.63, %arg.buffer.5.0
  %.65 = icmp slt i64 %.64, 0
  %.67 = and i1 %.66, %.65
  %.74 = select i1 %.67, i64 %arg.buffer.5.0, i64 0
  %.54.1 = add i64 %.74, %.63
  %.231 = icmp slt i64 %arg.slot, 0
  %.232 = select i1 %.231, i64 %arg.buffer.5.0, i64 0
  %0 = getelementptr i64, ptr %arg.buffer.4, i64 %arg.slot
  %.300 = icmp slt i64 %.54.1, 0
  %.301 = select i1 %.300, i64 %arg.buffer.5.0, i64 0
  %1 = getelementptr i64, ptr %arg.buffer.4, i64 %.54.1
  %xtraiter = and i64 %arg.iters, 7
  %lcmp.mod.not = icmp eq i64 %xtraiter, 0
  br i1 %lcmp.mod.not, label %B122.prol.loopexit, label %B122.prol.preheader

B122.prol.preheader:                              ; preds = %B122.lr.ph
  br label %B122.prol

B122.prol:                                        ; preds = %B122.prol.preheader, %B423.prol
  %lsr.iv1 = phi i64 [ %xtraiter, %B122.prol.preheader ], [ %lsr.iv.next2, %B423.prol ]
  %x.4.0114.prol = phi i64 [ %.213.prol, %B423.prol ], [ %.23, %B122.prol.preheader ]
  %.165109113.prol = phi i64 [ %.175.prol, %B423.prol ], [ %arg.iters, %B122.prol.preheader ]
  %.205.prol = shl i64 %x.4.0114.prol, 13
  %.207.prol = xor i64 %.205.prol, %x.4.0114.prol
  %.210.prol = lshr i64 %.207.prol, 7
  %.211.prol = xor i64 %.210.prol, %.207.prol
  %.212.prol = shl i64 %.211.prol, 17
  %.213.prol = xor i64 %.212.prol, %.211.prol
  %sunkaddr34 = mul i64 %.232, 8
  %sunkaddr35 = getelementptr i8, ptr %0, i64 %sunkaddr34
  %.247.prol = load i64, ptr %sunkaddr35, align 8
  %.249.prol = lshr i64 %.213.prol, 40
  %.250.prol = add i64 %.249.prol, %.247.prol
  store i64 %.250.prol, ptr %sunkaddr35, align 8
  %.282.prol = icmp eq i64 %.250.prol, -1
  br i1 %.282.prol, label %B410.prol, label %B423.prol

B410.prol:                                        ; preds = %B122.prol
  %sunkaddr36 = mul i64 %.301, 8
  %sunkaddr37 = getelementptr i8, ptr %1, i64 %sunkaddr36
  store i64 %.213.prol, ptr %sunkaddr37, align 8
  br label %B423.prol

B423.prol:                                        ; preds = %B410.prol, %B122.prol
  %lsr.iv.next2 = add nsw i64 %lsr.iv1, -1
  %.175.prol = add i64 %.165109113.prol, -1
  %prol.iter.cmp.not = icmp eq i64 %lsr.iv.next2, 0
  br i1 %prol.iter.cmp.not, label %B122.prol.loopexit, label %B122.prol, !llvm.loop !2

B122.prol.loopexit:                               ; preds = %B423.prol, %B122.lr.ph
  %x.4.0114.unr = phi i64 [ %.23, %B122.lr.ph ], [ %.213.prol, %B423.prol ]
  %.165109113.unr = phi i64 [ %arg.iters, %B122.lr.ph ], [ %.175.prol, %B423.prol ]
  %2 = icmp ult i64 %arg.iters, 8
  br i1 %2, label %B422, label %B122.preheader

B122.preheader:                                   ; preds = %B122.prol.loopexit
  %3 = add i64 %.165109113.unr, 8
  br label %B122
}