;
PRO PLOT_Scatter_Histograms_other, Filename,Nbins,X0_raw,X1_Raw,Y0_raw,Y1_Raw,Loglin
  ;
  ; Following looking for other X0, X1, Y0, Y1 connections
  ;
  PRINT,'In PLOT_Scatter_Histogram_other'
  Nb = Nbins
  
  Min1  = 0.5
  Max1  = 4.0
  Min2  = 0.5
  Max2  = 4.0
  Xrange1 = [Min1,Max1]
  Yrange1 = [Min2,Max2]

  Bin1 = (Max1 - Min1)/(Nb-1)
  Bin2 = (Max2 - Min2)/(Nb-1)

  H2D_b = HIST_2D(X0_raw,X1_Raw,MIN1=Min1,MAX1=Max1,MIN2=Min2,MAX2=Max2, BIN1=Bin1,BIN2=Bin2)
  PRINT,'SIZE(H2D_b)',SIZE(H2D_b)
  Info = SIZE(H2D_b); Need to do this because sometimes discrepancy in expected size of array
  Xdim = Info(1)
  Ydim = Info(2)
  XX = Min1+(Indgen(Xdim))*Bin1 + Bin1/2.0
  YY = Min2+(Indgen(Ydim))*Bin2 + Bin2/2.0

  NEvents = SIZE(X0_raw,/N_ELEMENTS)

  IF Loglin EQ 1 THEN  BEGIN
    H2D_b = ALOG10(H2D_b+.01)
    TITLE = Filename+",  # Events " + STRCOMPRESS(STRING(NEvents))+", Log Intensity"
  ENDIF ELSE BEGIN
    TITLE = Filename+",  # Events " + STRCOMPRESS(STRING(NEvents))+", Lin Intensity"
  ENDELSE

  nrow = 2
  ncol = 1
  L = 1
  c = CONTOUR(H2D_b,XX,YY, /FILL, ASPECT_RATIO=1, RGB_TABLE=39, $
    WINDOW_TITLE = 'Scatter Plot Histograms Other', $
    LOCATION = [0,800], $ ; [X offset, Y offset] giving the window's screen offset in pixels
    DIMENSIONS = [800,800], $ ;[width, height] to specify the window dimensions in pixels
    XRANGE = XRANGE1, XSTYLE = 1, $
    YRANGE = YRANGE1, YSTYLE = 1, $
    TITLE = Title, $
    XTITLE = 'X0_raw', $
    YTITLE = 'X1_raw', $
    LAYOUT=[ncol,nrow,L])





  H2D_c = HIST_2D(Y0_raw,Y1_raw,MIN1=Min1,MAX1=Max1,MIN2=Min2,MAX2=Max2, BIN1=Bin1,BIN2=Bin2)
  PRINT,'SIZE(H2D_c)',SIZE(H2D_c)
  Info = SIZE(H2D_c); Need to do this because sometimes discrepancy in expected size of array
  Xdim = Info(1)
  Ydim = Info(2)
  XX = Min1+(Indgen(Xdim))*Bin1 + Bin1/2.0
  YY = Min2+(Indgen(Ydim))*Bin2 + Bin2/2.0

  NEvents = SIZE(Y0_raw,/N_ELEMENTS)
  IF Loglin EQ 1 THEN  BEGIN
    H2D_c = ALOG10(H2D_c+.01)
    TITLE = Filename+", # Events " + STRCOMPRESS(STRING(NEvents))+", Log Intensity"
  ENDIF ELSE BEGIN
    TITLE = Filename+", # Events " + STRCOMPRESS(STRING(NEvents))+", Lin Intensity"
  ENDELSE

  L = L+1
  c = CONTOUR(H2D_c,XX,YY, /FILL, ASPECT_RATIO=1, RGB_TABLE=39, $
    LOCATION = [0,800], $ ; [X offset, Y offset] giving the window's screen offset in pixels
    DIMENSIONS = [800,800], $ ;[width, height] to specify the window dimensions in pixels
    XRANGE = XRANGE1, XSTYLE = 1, $
    YRANGE = YRANGE1, YSTYLE = 1, $
    TITLE = Title, $
    XTITLE = 'Y0_raw', $
    YTITLE = 'Y1_raw', $
    LAYOUT=[ncol,nrow,L],/CURRENT)

END
;
;************************************************************************************************

;************************************************************************************************
;
PRO PLOT_Scatter_Histogram,Filename,Nbins,X0,X1,Y0,Y1,Loglin
  ;
  ; Following are Histogram plots ; (Y0 + Y1) v (X0 + X1)
  ;
;  common wtem
;  common wtdata
  PRINT,'In PLOT_Scatter_Histogram'

  Nb = Nbins

  Min1  = 0.0
  Max1  = 5.0
  Min2  = 0.0
  Max2  = 5.0
  Xrange1 = [Min1,Max1]
  Yrange1 = [Min2,Max2]

  Bin1 = (Max1 - Min1)/(Nb-1)
  Bin2 = (Max2 - Min2)/(Nb-1)

  X0pX1 = X0+X1
  Y0pY1 = Y0+Y1

  H2D_a = HIST_2D(X0pX1,Y0pY1,MIN1=MIN1,MAX1=MAX1,Min2=MIN2,MAX2=MAX2, bin1=Bin1,bin2=Bin2)
  PRINT,'SIZE(H2D_a)',SIZE(H2D_a)
  Info = SIZE(H2D_a); Need to do this because sometimes discrepancy in expected size of array
  Xdim = Info(1)
  Ydim = Info(2)
  XX = Min1+(Indgen(Xdim))*Bin1 + Bin1/2.0
  YY = Min2+(Indgen(Ydim))*Bin2 + Bin2/2.0


  NEvents = SIZE(XP0,/N_ELEMENTS)

  IF Loglin EQ 1 THEN  BEGIN
    H2D_a = ALOG10(H2D_a+.1)
    TITLE = Filename+",  # Events " + STRCOMPRESS(STRING(NEvents))+", Log Intensity"
  ENDIF ELSE BEGIN
    TITLE = Filename+",  # Events " + STRCOMPRESS(STRING(NEvents))+", Lin Intensity"
  ENDELSE

  nrow = 1
  ncol = 1
  L = 1
  c = CONTOUR(H2D_a,XX,YY, /FILL, ASPECT_RATIO=1, RGB_TABLE=39, $
    WINDOW_TITLE = 'Scatter Plot Histogram', $
    LOCATION = [100,100], $ ; [X offset, Y offset] giving the window's screen offset in pixels
    DIMENSIONS = [800,800], $ ;[width, height] to specify the window dimensions in pixels
    XRANGE = XRANGE1, XSTYLE = 1, $
    YRANGE = YRANGE1, YSTYLE = 1, $
    TITLE = Title, $
    XTITLE = 'X(0,*)+X(1,*)', $
    YTITLE = 'Y(0,*)+Y(1,*)', $
    LAYOUT=[ncol,nrow,L])

  Result = LINFIT(X0pX1,Y0pY1,CHISQR=CHISQR,PROB=PROB,SIGMA=SIGMA,YFIT=YFIT)

  m    = Result[1]
  c    = Result[0]
  Lab1 = "m = "+STRCOMPRESS(STRING(m,FORMAT='(F5.3)'),/remove_all)
  Lab2 = " c = "+STRCOMPRESS(STRING(c,FORMAT='(F6.3)'),/remove_all)
  Lab3 = " CHISQ = "+STRCOMPRESS(STRING(CHISQR,FORMAT='(F8.1)'),/remove_all)
  Lab4 = " PROB = "+STRCOMPRESS(STRING(PROB,FORMAT='(F5.3)'),/remove_all)

  Plot3Fit  = PLOT(X0pX1,YFIT,Color='black',Thick=1, /OVERPLOT,$
    NAME=Lab1+Lab2+Lab3+Lab4)
  Leg       = LEGEND(TARGET=[Plot3Fit],  Position=[.6,1.0],/NORMAL,FONT_SIZE=10)
END
;
;************************************************************************************************

PRO PLOT_Contour_All,Filename,Nbins,XP0,YP0
  MAX1 = 1.0
  MIN1 = 0.0
  MAX2 = 1.0
  MIN2 = 0.0

  BINSIZE1 = (MAX1 - MIN1)/(NBINS-1)
  BINSIZE2 = (MAX2 - MIN2)/(NBINS-1)

  ;  H2D_d = HIST_2D(XP4,YP4,MIN1=MIN1,MAX1=MAX1,Min2=MIN2,MAX2=MAX2, bin1=BINSIZE1,bin2=BINSIZE2)
  H2D_d = HIST_2D(XP0,YP0,MIN1=MIN1,MAX1=MAX1,Min2=MIN2,MAX2=MAX2, bin1=BINSIZE1,bin2=BINSIZE2)
  H2D_d_Log = ALOG10(H2D_d+.01)
  nrow = 1
  ncol = 1
  L = 0
  L = L+1

  PRINT,'In PLOT_Contour_All"
  PRINT,'SIZE(H2D_d)',SIZE(H2D_d)

  SZ = SIZE(H2D_d)        ; If NBINS = 501 say, SIZE(H2D_d) = NBINS-1 so check dims then create XX, YY
  PRINT,'SIZE(H2D_d)',SZ
  PRINT,'N Dimensions =', SZ(0)
  PRINT,' First Dim = ',SZ(1)
  PRINT,' Second Dim = ',SZ(2)

  XX = MIN1 +(MAX1-MIN1)*FINDGEN(SZ(1))/(SZ(1)-1)
  YY = MIN2 +(MAX2-MIN2)*FINDGEN(SZ(2))/(SZ(2)-1)

  XRANGE2 = [0.0,1.0]
  YRANGE2 = [0.0,1.0]
  NEvents = SIZE(XP4,/N_Elements)
  TITLE = Filename+",  # Events " + STRCOMPRESS(STRING(NEvents))+" Norm"
  c = CONTOUR(H2D_d,XX,YY, /FILL, ASPECT_RATIO=1, RGB_TABLE=39, $
    WINDOW_TITLE = 'Contour All', $
    LOCATION = [0,800], $ ; [X offset, Y offset] giving the window's screen offset in pixels
    DIMENSIONS = [800,800], $ ;[width, height] to specify the window dimensions in pixels
    XRANGE = XRANGE2, XSTYLE = 1, $
    YRANGE = YRANGE2, YSTYLE = 1, $
    TITLE = Title, $
    XTITLE = 'X(1,*)/(X(0,*)+X(1,*))', $
    YTITLE = 'Y(1,*)/(Y(0,*)+Y(1,*))', $
    LAYOUT=[ncol,nrow,L])
END
;
;************************************************************************************************
;
PRO PLOT_Contour_Panels,Filename,PHD,Xp0,Yp0,Nbins,Acc_Time,Loglin
 ; common wtdata
  PRINT,'In PLOT_Contour_Panels'

  LTH_A = MAKE_ARRAY(12)
  UTH_A = MAKE_ARRAY(12)

  LTH_A(0) = 0              ; 0-3
  UTH_A(0) = LTH_A(0) + 3

  LTH_A(1) = UTH_A(0)       ; 3-4
  UTH_A(1) = LTH_A(1) + 1

  LTH_A(2) = UTH_A(1)       ; 4-5
  UTH_A(2) = LTH_A(2) + 1

  LTH_A(3) = UTH_A(2)       ; 5-6
  UTH_A(3) = LTH_A(3) + 1

  LTH_A(4) = UTH_A(3)       ; 6-7
  UTH_A(4) = LTH_A(4) + 1

  LTH_A(5) = UTH_A(4)       ; 7-8
  UTH_A(5) = LTH_A(5) + 1

  LTH_A(6) = UTH_A(5)       ; 8-9
  UTH_A(6) = LTH_A(6) + 1

  LTH_A(7) = UTH_A(6)       ; 9-12
  UTH_A(7) = LTH_A(7) + 3

  nrow = 2
  ncol = 4
  npan = 8

  L = 0

  FOR P = 0,npan-1 DO BEGIN
    PRINT,"###################################################"
    PRINT,'P = ',P
    L=L+1
    LTH = LTH_A(P)
    UTH = UTH_A(P)
    Big = WHERE((PHD GE LTH) AND (PHD LE UTH),Count) ; Take subset of data
    PC = 100.0*Count/SIZE(PHD,/N_ELEMENTS)
    PRINT,'LTH, UTH, % ',LTH,UTH,PC

    ; Counts/sec in this PHD range
    CPS = Count/Acc_Time

    MAX1 = 1.0
    MIN1 = 0.0
    MAX2 = 1.0
    MIN2 = 0.0

    ;  NBINS = 501
    ;  MAX1 = 0.6
    ;  MIN1 = 0.2
    ;  MAX2 = 0.7
    ;  MIN2 = 0.3

    BINSIZE1 = (MAX1 - MIN1)/(NBINS-1)
    BINSIZE2 = (MAX2 - MIN2)/(NBINS-1)
    XXX = MIN1 +(MAX1-MIN1)*FINDGEN(NBins)/(NBINS-1)
    YYY = MIN2 +(MAX2-MIN2)* FINDGEN(NBins)/(NBINS-1)

    PRINT,"P,Count",P,Count
    IF Count GT 1 THEN BEGIN
      ;  H2D_e = HIST_2D(XP4(Big),YP4(Big),MIN1=MIN1,MAX1=MAX1,Min2=MIN2,MAX2=MAX2, bin1=BINSIZE1,bin2=BINSIZE2)
      H2D_e = HIST_2D(XP0(Big),YP0(Big),MIN1=MIN1,MAX1=MAX1,Min2=MIN2,MAX2=MAX2, bin1=BINSIZE1,bin2=BINSIZE2)

      Sz = SIZE(H2d_e)
      NXdim = Sz(1)
      NYdim = Sz(2)
      Print,Sz
      PRINT,"NXDIM,NYBIM",NXDIM,NYDIM
      MAXV = MAX(H2D_e)
      H2D_Tmp = H2d_e
      H2D_SM = H2d_e
 
      Misc4 = 1 
      NS = Misc4 ; # times to run smoothing, my 2D version of 3pt smooth
      PRINT,"Ns = ",NS
      FOR INS = 1, NS DO BEGIN
        FOR IX = 1, NXdim-2 DO BEGIN
          FOR IY = 1, NYdim-2 DO BEGIN
            ;        H2D_SM(IX,IY) = (H2D_TMP(IX-1,IY-1) + H2D_TMP(IX,IY-1) + H2D_TMP(IX+1,IY-1) + $ ; center + 8 nearest neighbors
            ;          H2D_TMP(IX-1,IY)   + 2.0*H2D_TMP(IX,IY) + H2D_TMP(IX+1,IY)   + $
            ;          H2D_TMP(IX-1,IY+1) + H2D_TMP(IX,IY+1) + H2D_TMP(IX+1,IY+1))/9.0

            H2D_SM(IX,IY) =  (H2D_TMP(IX,IY-1) + $ ; center + 4 nearest neighbors
              H2D_TMP(IX-1,IY)   + 2.0*H2D_TMP(IX,IY) + H2D_TMP(IX+1,IY)   + $
              H2D_TMP(IX,IY+1))/6.0

          ENDFOR
        ENDFOR
        H2D_TMP = H2D_SM
      ENDFOR
      h2d_e = H2D_TMP
      IF LogLin EQ 1 THEN   h2d_e = ALOG10(h2d_e+.1)

      SZ = SIZE(H2D_e)        ; If NBINS = 501 say, SIZE(H2D_d) = NBINS-1 so check dims then create XX, YY
      PRINT,'SIZE(H2D_e)',SZ
      PRINT,'N Dimensions =', SZ(0)
      PRINT,' First Dim = ',SZ(1)
      PRINT,' Second Dim = ',SZ(2)

      XX = MIN1 +(MAX1-MIN1)*FINDGEN(SZ(1))/(SZ(1)-1)
      YY = MIN2 +(MAX2-MIN2)*FINDGEN(SZ(2))/(SZ(2)-1)
      ;  XRANGE=[0.0,1.]
      ;  YRANGE=[0.0,1.]

      XRANGE=[0.35,0.55]
      YRANGE=[0.4,0.6]

      NEvents = SIZE(XP0,/N_Elements)

      LTH_STR = STRCOMPRESS(STRING(LTH,FORMAT='(F4.2)'),/remove_all)
      UTH_STR = STRCOMPRESS(STRING(UTH,FORMAT='(F5.2)'),/remove_all)
      PC_STR = STRCOMPRESS(STRING(PC,FORMAT='(F5.2)'),/remove_all)
      CPS_STR = STRCOMPRESS(STRING(CPS,FORMAT='(F7.2)'),/remove_all)
      TITLE = "CPS " + CPS_STR + ", " + LTH_STR + ", " + UTH_STR + ",  " + PC_STR + "%"

      PRINT,TITLE
      IF P EQ 0 THEN BEGIN
      c = CONTOUR(H2D_e,XX,YY, /FILL, ASPECT_RATIO=1, RGB_TABLE=39, $
        WINDOW_TITLE = 'Contour Panels', $
        LOCATION = [0,0], $ ; [X offset, Y offset] giving the window's screen offset in pixels
        DIMENSIONS = [1700,1100], $ ;[width, height] to specify the window dimensions in pixels
        XRANGE = XRANGE, XSTYLE = 1, $
        YRANGE = YRANGE, YSTYLE = 1, $
        TITLE = TITLE , $
        XTITLE = 'X1 / (X0 + X1)', $
        YTITLE = 'Y1 / (Y0 + Y1)', $
        LAYOUT=[ncol,nrow,L])
      ENDIF
      IF P NE 0 THEN BEGIN
        c = CONTOUR(H2D_e,XX,YY, /FILL, ASPECT_RATIO=1, RGB_TABLE=39, $
          WINDOW_TITLE = 'Contour Panels', $
          LOCATION = [0,0], $ ; [X offset, Y offset] giving the window's screen offset in pixels
          DIMENSIONS = [1700,1100], $ ;[width, height] to specify the window dimensions in pixels
          XRANGE = XRANGE, XSTYLE = 1, $
          YRANGE = YRANGE, YSTYLE = 1, $
          TITLE = TITLE , $
          XTITLE = 'X1 / (X0 + X1)', $
          YTITLE = 'Y1 / (Y0 + Y1)', $
          LAYOUT=[ncol,nrow,L],/CURRENT)
      ENDIF
      
    ENDIF
  ENDFOR
END
;
;************************************************************************************************
PRO PLOT_Pulse_Height_Dist,Filename,PHD,NBINS,D
 ; common wtdata
  ;
  ; Plot Pulse Height Distributions
  ;
  MinV = 0.
  MaxV = 14.0
  Nbins = 1+(MaxV-MinV)*100 ;e.g. 1401

  PRINT,'In PLOT_Pulse_Height_Dist'
  PRINT,'MIN(PHD),MAX(PHD)',MIN(PHD),MAX(PHD)
  XVals = MinV + (MaxV-MinV)*FINDGEN(NBins)/(Nbins-1)
  PHDH = HISTOGRAM(PHD,Min=MinV, Max=MaxV, NBINS=Nbins);Binsize = 0.1,Locations = binvals)
  PRINT,"SIZE(PHD,N_ELEMENTS) ",SIZE(PHD,/N_ELEMENTS)
  PRINT,"SIZE(PHDH,N_ELEMENTS) ",SIZE(PHDH,/N_ELEMENTS)
  PRINT,"MAX(PHDH) ",MAX(PHDH)

  XRANGE=[MinV,MaxV]
  YRANGE=[MIN(phdh),MAX(phdh)]
  NEvents = SIZE(PHD,/N_Elements)

  TITLE = Filename+",  # Events " + STRCOMPRESS(STRING(NEvents))+", Pulse Height Dist."
  nrow = 2
  ncol = 2
  L = 1
  histoplot = plot(Xvals,phdh, /STAIRSTEP, $
    WINDOW_TITLE = 'Pulse_Height_Dist', $
    LOCATION = [0,800], $ ; [X offset, Y offset] giving the window's screen offset in pixels
    DIMENSIONS = [1200,1000], $ ;[width, height] to specify the window dimensions in pixels
    XRANGE=XRange,XSTYLE=1,$
    ;    YRANGE=YRANGE,YSTYLE=0,YLOG=0,$
    YLOG=0,$
    TITLE = Title ,$
    XTitle = 'PHD = X0+X1+Y0+Y1',$
    Ytitle = 'Frequency (Lin)', $
    LAYOUT=[ncol,nrow,L]); LEXI Anode

  L = 2
  histoplot = plot(Xvals,phdh, /STAIRSTEP, $
    WINDOW_TITLE = 'Pulse_Height_Dist', $
    LOCATION = [0,800], $ ; [X offset, Y offset] giving the window's screen offset in pixels
    DIMENSIONS = [1200,1000], $ ;[width, height] to specify the window dimensions in pixels
    XRANGE=XRange,XSTYLE=1,$
    ;    YRANGE=YRANGE,YSTYLE=0,YLOG=0,$
    YLOG=1,$
    TITLE = Title ,$
    XTitle = 'PHD = X0+X1+Y0+Y1',$
    Ytitle = 'Frequency (Log)', $
    LAYOUT=[ncol,nrow,L],/Current); LEXI Anode

  ; LEXI Anode
  H0_Raw = D(0,*) ; X0 Wide Strip LHS      Ver 5 Anode Board J1
  H1_Raw = D(2,*) ; X1 Wide Strip RHS      Ver 5 Anode Board J3
  H2_Raw = D(3,*) ; Y0 Wedge Pointing Up   Ver 5 Anode Board J4
  H3_Raw = D(1,*) ; Y1 Wedge Pointing Down Ver 5 Anode Board J2

  MinV = 0.
  MaxV = 5.0
  Nbins = 1+(MaxV-MinV)*100 ; e.g. 501

  PHDH0 = HISTOGRAM(H0_Raw,Min=MinV, Max=MaxV, NBINS=Nbins);Binsize = 0.1,Locations = binvals)
  PHDH1 = HISTOGRAM(H1_Raw,Min=MinV, Max=MaxV, NBINS=Nbins);Binsize = 0.1,Locations = binvals)
  PHDH2 = HISTOGRAM(H2_Raw,Min=MinV, Max=MaxV, NBINS=Nbins);Binsize = 0.1,Locations = binvals)
  PHDH3 = HISTOGRAM(H3_Raw,Min=MinV, Max=MaxV, NBINS=Nbins);Binsize = 0.1,Locations = binvals)
  H_ALL = [PHDH0,PHDH1,PHDH2,PHDH3]

  XRANGE=[MinV,MaxV]
  YRANGE=[0,MAX(H_ALL)*1.1]

  PRINT,"SIZE(H3_Raw,N_ELEMENTS) ",SIZE(H3_Raw,/N_ELEMENTS)
  PRINT,"SIZE(PHDH3,N_ELEMENTS) ",SIZE(PHDH3,/N_ELEMENTS)
  PRINT,"MAX(PHDH3) ",MAX(PHDH3)

  FF = 0
  LL = NBins -1
  ; (FF:LL) to avoid 'Flyback' last point goes back to 0
  L = 3
  histoplot0 = plot(Xvals(FF:LL),Phdh0(FF:LL),Color='red',Thick=1, /STAIRSTEP, $
    XRANGE=XRange,XSTYLE=1,$
    YRANGE=YRANGE,YLOG=0,$
    TITLE = Title ,$
    XTitle = 'X0 red, X1 green, Y0 blue, Y1 orange  (RAW)',$

    Ytitle = 'Frequency (Lin)', $
    LAYOUT=[ncol,nrow,L],/Current)

  ;  HISTOPLOT0 = PLOT(Xvals(F:L),Phdh0(F:L),Color='red',Thick=1, /STAIRSTEP,/OVERPLOT);,$
  ;    NAME=Lab1+Lab2)

  HISTOPLOT1 = PLOT(Xvals(FF:LL),Phdh1(FF:LL),Color='green',Thick=1, /STAIRSTEP,/OVERPLOT);,$
  HISTOPLOT2 = PLOT(Xvals(FF:LL),Phdh2(FF:LL),Color='blue',Thick=1, /STAIRSTEP,/OVERPLOT);,$
  HISTOPLOT3 = PLOT(Xvals(FF:LL),Phdh3(FF:LL),Color='orange',Thick=1, /STAIRSTEP,/OVERPLOT);,$

  L = 4
  histoplot00 = plot(Xvals(FF:LL),Phdh0(FF:LL),Color='red',Thick=1, /STAIRSTEP, $
    XRANGE=XRange,XSTYLE=1,$
    YRANGE=YRANGE,YLOG=1,$
    TITLE = Title ,$
    XTitle = 'X0 red, X1 green, Y0 blue, Y1 orange  (RAW)',$
    Ytitle = 'Frequency (Log)', $
    LAYOUT=[ncol,nrow,L],/Current)

  HISTOPLOT11 = PLOT(Xvals(FF:LL),Phdh1(FF:LL),Color='green',Thick=1, /STAIRSTEP,/OVERPLOT);,$
  HISTOPLOT22 = PLOT(Xvals(FF:LL),Phdh2(FF:LL),Color='blue',Thick=1, /STAIRSTEP,/OVERPLOT);,$
  HISTOPLOT33 = PLOT(Xvals(FF:LL),Phdh3(FF:LL),Color='orange',Thick=1, /STAIRSTEP,/OVERPLOT);,$
END
;
;************************************************************************************************

PRO PLOT_Counts_Time,Filename,Tm,Phd
;  common wtdata
  PRINT,'In PLOT_PCounts_Time"
  NEvents = SIZE(PHD,/N_Elements)
  PRINT,"NEvents ",NEvents
  Nbins=10000
  TmRate_All = HISTOGRAM(Tm,Min=0,BINSIZE=1)

  XRange = [Min(Tm),MAX(Tm)]
  PRINT,"SIZE(TmRate_All) ",SIZE(TmRate_All)
  PRINT,"Xrange ",Xrange
  ;  PLOT,TmRate_All
  ;  STOP
  nrow = 2
  ncol = 1
  L = 1

  SmLim = .25
  BigLim = 3.0

  SmLim = 2
  BigLim = 8

  Big_Idx = WHERE((PHD GT BigLim),Count) ; Take subset of data
  Percent_Big = Count*100.0/NEvents
  N_Big = Count

  Med_Idx = WHERE((PHD GE SmLim)AND (PHD LE BigLim),Count) ; Take subset of data
  Percent_Med = Count*100.0/NEvents
  N_Med = Count

  Small_Idx = WHERE((PHD LT SmLim),Count) ; Take subset of data
  Percent_Small = Count*100.0/NEvents
  N_Small = Count
  PRINT,"N_Big, N_Med, N_Small ",N_Big, N_Med, N_Small 
  
  Lab1 = 'Small < '+STRCOMPRESS(STRING(SmLim,FORMAT='(F4.2)'),/remove_all)+"  " $
    +STRCOMPRESS(STRING(Percent_Small,FORMAT='(F5.1)'),/remove_all)+"%"

  Lab2 = 'Med '+STRCOMPRESS(STRING(SmLim,FORMAT='(F4.2)'),/remove_all)+" " $
    +STRCOMPRESS(STRING(BigLim,FORMAT='(F3.1)'),/remove_all) +"  " $
    +STRCOMPRESS(STRING(Percent_Med,FORMAT='(F5.1)'),/remove_all)+"%"

  Lab3 = 'Pulse > '+STRCOMPRESS(STRING(BigLim,FORMAT='(F4.2)'),/remove_all)+"  " $
    +STRCOMPRESS(STRING(Percent_Big,FORMAT='(F5.1)'),/remove_all)+"%"

  Lab4 = 'All Pulses,  100%'

  Th=1
  Yrange = [0,100]
  
  TITLE = Filename+",  # Events v. Time,  total # " + STRCOMPRESS(STRING(NEvents))
  Counts_Time = plot(TmRate_All,Color='black',Thick=Th, /STAIRSTEP, $
    WINDOW_TITLE = 'Counts_Time', $
    LOCATION = [50,600], $ ; [X offset, Y offset] giving the window's screen offset in pixels
    DIMENSIONS = [1200,1000], $ ;[width, height] to specify the window dimensions in pixels
    XRANGE=XRange,XSTYLE=1,$
      YRANGE=YRANGE,YSTYLE=1,YLOG=0,$
    TITLE = Title ,$
    XTitle = 'Time (Sec.) "as reported" ',$
    Ytitle = 'Frequency', $
    NAME= Lab4 , $
    LAYOUT=[ncol,nrow,L])

  PRINT,"N_Big ",N_Big
  IF N_Big GT 1 THEN BEGIN
    TmRate_Big = HISTOGRAM(Tm(Big_Idx),Min=0,BINSIZE=1)
    Counts_Big = PLOT(TmRate_Big,Color='red',Thick=Th, /OVERPLOT, /STAIRSTEP,NAME = Lab3 );,$
  ENDIF

  PRINT,"N_Med ",N_Med
  IF N_Med GT 1 THEN BEGIN
    TmRate_Med = HISTOGRAM(Tm(Med_Idx),Min=0,BINSIZE=1)
    Counts_Med = PLOT(TmRate_Med,Color='green',Thick=Th, /OVERPLOT, /STAIRSTEP,NAME = Lab2 );,$
  ENDIF

  PRINT,"N_Small ",N_Small
  IF N_Small GT 1 THEN BEGIN
    TmRate_Small = HISTOGRAM(Tm(Small_Idx),Min=0,BINSIZE=1)
    Counts_Small = PLOT(TmRate_Small,Color='blue',Thick=Th, /OVERPLOT, /STAIRSTEP, NAME=Lab1 );,$
  ENDIF

  Leg = LEGEND(TARGET=[Counts_Time,Counts_Big,Counts_Med,Counts_Small], Position=[.4,.8],/NORMAL)

  L = 2
  Xt = FINDGEN(NEvents)
  TITLE = Filename+",  # Events v. Time,  total # " + STRCOMPRESS(STRING(NEvents))
  histoplot = plot(Xt,Tm, LINESTYLE=6, COLOR='red',SYMBOL='dot', $ $
    ; XRANGE=XRange,XSTYLE=1,$
    ;  YRANGE=YRANGE,YSTYLE=1,YLOG=0,$
    TITLE = Title ,$
    XTitle = 'Event # (Line in File)',$
    Ytitle = 'Time ', $
    LAYOUT=[ncol,nrow,L],/CURRENT)

  GOTO,Skip_Hi_res
  ;
  ; Now plot High res.. Counts as fm fraction of second
  ;
  TmSecReal = Tm - FIX(Tm)
  PRINT,'Min(TmSecReal),Max(TmSecReal)',Min(TmSecReal),Max(TmSecReal)
  Binsize = 1./1024.

  TmSecReal_All = HISTOGRAM(TmSecReal,Min=0, Max=1,Binsize=Binsize)
  NVals = SIZE(TmSecReal_All,/N_ELEMENTS)
  Xvals = FINDGEN(NVals)*0.001

  XRange=[0,1.20]
  YRange=[0,MAX(TmSecReal_All)]

  One_Sec_All2 = plot(XVals,TmSecReal_All,Color= 'black',Thick=Th, /STAIRSTEP, $
    WINDOW_TITLE = 'One_Sec_Data', $
    LOCATION = [50,600], $ ; [X offset, Y offset] giving the window's screen offset in pixels
    DIMENSIONS = [1200,1000], $ ;[width, height] to specify the window dimensions in pixels
    XRANGE = XRange,XSTYLE=1,$
    YRANGE = YRANGE,YSTYLE=1,YLOG=0,$
    TITLE = Title ,$
    XTitle = '~ One Sec - aliasing',$
    Ytitle = 'Frequency', $
    NAME= Lab4 );, $
  ;  LAYOUT=[ncol,nrow,L]))

  Med_Idx = WHERE((PHD GE SmLim)AND (PHD LE BigLim),Count) ; Take subset of data
  ; Needs more work here

  TmSecReal_Med = HISTOGRAM(TmSecReal(Med_Idx),Min=0, Max=1,Binsize=Binsize)
  NVals2 = SIZE(TmSecReal_Med,/N_ELEMENTS)
  Xvals2 = FINDGEN(NVals2)*0.001
  Counts_Med = PLOT(XVals2,TmSecReal_Med,Color='green',Thick=Th, /OVERPLOT, /STAIRSTEP,NAME = Lab2 );,$

  TmSecReal_Big = HISTOGRAM(TmSecReal(Big_Idx),Min=0, Max=1,Binsize=Binsize)
  NVals3 = SIZE(TmSecReal_Big,/N_ELEMENTS)
  Xvals3 = FINDGEN(NVals3)*0.001
  Counts_Big = PLOT(XVals2,TmSecReal_Big,Color='red',Thick=Th, /OVERPLOT, /STAIRSTEP,NAME = Lab2 );,$

  TmSecReal_Small = HISTOGRAM(TmSecReal(Small_Idx),Min=0, Max=1,Binsize=Binsize)
  NVals3 = SIZE(TmSecReal_Small,/N_ELEMENTS)
  Xvals3 = FINDGEN(NVals3)*0.001
  Counts_Small = PLOT(XVals3,TmSecReal_Small,Color='blue',Thick=Th, /OVERPLOT, /STAIRSTEP,NAME = Lab2 );,$

  Skip_Hi_res: ;

END
;
;************************************************************************************************

PRO Read_File,Filename,Dat,Tm,Z0min,Z1min,Z2min,Z3min,Events
  ;#############################################################################
  ;## Pro Read_File   ##########################################################
  ;#############################################################################

  USERPROFILE = GETENV("USERPROFILE")
  PATH = 'C:\Users\' ; Change to location of data files


  Fn = DIALOG_PICKFILE(/READ,FILTER=['*.CSV'], $
    ;   FILE="TEST.CSV", $
    Path = PATH                          , $  ; Initial Path
    Multiple_Files = 1                   , $
    Get_Path = CSV_Dir                   , $
    Title = "Read Labview *.CSV file(s)" )


  Size_Fn = SIZE(Fn)
  PRINT,"Size_Fn",Size_Fn

  ;  Fn = DIALOG_PICKFILE(TITLE="Read Wedge_Strip Data FIle",PATH=PATH)

  IF (Fn EQ "") THEN BEGIN
    Print,"No File Selected"
  ENDIF

  Line        = STRARR(1)
  Line        = ""
  RAW         = 0
  AnodeType   = 0 ; 0 = Cupid, 1 = LEXI

  IF (FN NE "") THEN BEGIN
    PRINT, "File Selected ",Fn

    L_Slash   = STRPOS(Fn,"\",/REVERSE_SEARCH)  ; Pos \
    Filernlen = STRLEN(Fn)            ; File name length
    LenFN     = Filernlen-L_Slash-1
    Filename  = STRMID( fn, RSTRPOS(fn, '\' ) + 1, LenFN ) ; Just File

    Nlines = file_lines(Fn) ;# Lines in file

    GET_LUN,UnitR
    OPENR,UnitR,FN,ERROR=err
    IF (err NE 0) THEN PRINT, "Error Opening ",FN

    Events = Nlines-1
    READF,Unitr,Line
    FirstChr = STRMID(Line,0,1)

    ;IF FirstChr is "C" then STORM data file from B34, No time
    ;IF FirstChr is "#" then Cupid Data
    ;IF neither, assume STORM data
    ;
    ; 2021_05_05 - 4 Cols data, Keller Probe
    ;Channel1,Channel2,Channel3,Channel4
    ;
    ; 2021_05_11 - 4 Cols data
    ;Channel1,Channel2,Channel3,Channel4,In_RangeX,In_RangeY


    ; 2021_05_18 to 2021_06_22 - 4 cols of data
    ;Eventime,Channel1,Channel2,Channel3,Channel4,In_RangeX,In_RangeY
    ;
    ; 2021_06_29 to 2021_07_14 - 5 cols of data, Timesramp is last col!
    ;Timestamp,Channel1,Channel2,Channel3,Channel4
    ;
    ; 2021_07_15 in Norms lab, Time stamp now at start, Keller Probe
    ;Timestamp,Channel1,Channel2,Channel3,Channel4

    IF Filename EQ 'storm_data_4_15_2011_2.txt' THEN BEGIN
      Events = 395387.0
      Events = 39538.0    ; for quick look
    ENDIF

    IF FirstChr EQ "C" OR FirstChr EQ "E" THEN BEGIN
      AnodeType = 1 ; LEXI
      D = FLTARR(4,Events)  ; Origninal 4 cols data from B34
      PRINT,"Reading ",FN," N_events = ",Events
      READF,UnitR,D
      PRINT,"Done reading in array"
      File_Loaded = true
      CLOSE,UnitR
      TM = FINDGEN(Events)/100.0  ; pretend time
    ENDIF

    IF (FirstChr EQ "T") OR (FirstChr EQ "#")  THEN BEGIN
      IF FirstChr EQ "T" THEN BEGIN ; Newer LEXI files with time
        AnodeType = 1 ; LEXI
      ENDIF
      IF FirstChr EQ "#" THEN BEGIN
        AnodeType = 0 ; Cupid
      ENDIF

      ; Bad data at Line l277577
      ;3680.58800,65535.00000,65214.00000,64927.00000,65131.00000
      ;675283.00000,10574.00000,63945.00000,63701.00000,63207.00000
      ;3680.59000,63945.00000,63701.00000,63207.00000,63542.00000
      ; Will omit all data tith Times GT 9999
      ;
      ; Limit # events for programming effort
      ;     events = 21000
      ;     events = 210000

      E = FLTARR(5,Events)  ; Time included and commas, from s/c
      D = FLTARR(4,Events)
      PRINT,"Reading ",FN," N_events = ",Events
      READF,UnitR,E
      PRINT,"Done reading in array"
      FOR I = 0, 2 DO BEGIN
        PRINT,E(0,I),E(1,I),E(2,I),E(3,I),E(4,I)
      ENDFOR
      File_Loaded = 1
      CLOSE,UnitR

      Raw = STRPOS(Filename,'RAW')  ; Determine if RAW data by looking at file name
      IF Raw GT 0 THEN BEGIN
        D(0:3,*) =  E(1:4,*)/10000.0
        Tm       =  E(0,*)  ; Time
        Min_all = 14677.  ;/14563.0
        D(0,*)  = (D(0,*) )/1.45630
        D(1,*)  = (D(1,*) )/1.45630
        D(2,*)  = (D(2,*) )/1.45630
        D(3,*)  = (D(3,*) )/1.45630
        Min_ini = 1.0 * 14677.0/14563.0
        Max_ini = 4.5
        Min_PHD = 0.5
        Max_PHD = 3.0
      ENDIF   ; Filtered Data

      IF AnodeType EQ 0 THEN BEGIN  ; Cupid
        D(0:3,*) = E(1:4,*)
        Tm       =  E(0,*)  ; Time
        Min_ini = 1.000
        Max_ini = 3.500
        Min_PHD = 0.0
        Max_PHD = 3.0
      ENDIF

      IF AnodeType EQ 1 THEN BEGIN  ; LEXI
        ; Determine which col is time, different version of data collection prog.
        AvPH = (E(1,0)+E(1,1)+E(1,2))/3.0

        IF E(0,0) GT AvPH*10.0 THEN BEGIN
          D(0:3,*) = E(1:4,*)
          Tm       =  E(0,*)/1000.0  ; Time in msec to sec
        ENDIF ELSE BEGIN
          D(0:3,*) = E(0:3,*)
          Tm       =  E(4,*)/1000.0  ; Time in msec to sec
        ENDELSE

        Min_ini = 1.250
        Max_ini = 3.35
        Min_PHD = 5.0 ; Restrict now for high res plots
        Max_PHD = 6.0
      ENDIF

      PRINT,"SIZE(E) ",SIZE(E)
      PRINT,"SIZE(D) ",SIZE(D)
      PRINT,"First 3 lines"
      FOR I = 0, 2 DO BEGIN
        PRINT,D(0,I),D(1,I),D(2,I),D(3,I)
      ENDFOR

      TotTime = Tm(Events-1)-Tm(0)

      FirstEvents = MIN([20000,Events])
      PRINT,"FirstEvents ",FirstEvents

      MinD0 = MIN(D(0,0:FirstEvents-1))
      MaxD0 = MAX(D(0,0:FirstEvents-1))

      MinD1 = MIN(D(1,0:FirstEvents-1))
      MaxD1 = MAX(D(1,0:FirstEvents-1))

      MinD2 = MIN(D(2,0:FirstEvents-1))
      MaxD2 = MAX(D(2,0:FirstEvents-1))

      MinD3 = MIN(D(3,0:FirstEvents-1))
      MaxD3 = MAX(D(3,0:FirstEvents-1))

      Min_all = MIN([MinD0,MinD1,MinD2,MinD3])
      Max_all = MAX([MaxD0,MaxD1,MaxD2,MaxD3])

      MinD0 = MIN(D(0,*))
      MaxD0 = MAX(D(0,*))

      MinD1 = MIN(D(1,*))
      MaxD1 = MAX(D(1,*))

      MinD2 = MIN(D(2,*))
      MaxD2 = MAX(D(2,*))

      MinD3 = MIN(D(3,*))
      MaxD3 = MAX(D(3,*))

      IDXN = WHERE((D(0,*) LT 0) OR (D(1,*) LT 0) OR (D(2,*) LT 0) OR (D(3,*) LT 0),Count)

      IDXP = WHERE((D(0,*) GE 0) AND (D(1,*) GE 0) AND (D(2,*) GE 0) AND (D(3,*) GE 0),Count)


      ; Remove the -ve values
      TT      = TM(IDXP)
      DD      = FLTARR(4,Count)
      DD(0,*) = D(0,IDXP)
      DD(1,*) = D(1,IDXP)
      DD(2,*) = D(2,IDXP)
      DD(3,*) = D(3,IDXP)
      D       = DD
      Tm      = TT

      ;
      ; Remove those with bad times
      ;      IBadT = WHERE(Tm GT 9999,Count)
      ;      PRINTBOX,WTEM_TXT,"#Bad Times "+STRING(Count)
      ;      IGoodT = WHERE(Tm LT 9999,Count)
      ;      PRINTBOX,WTEM_TXT,"#Good Times "+STRING(Count)

      ;      DD      = FLTARR(4,Count)
      ;      DD(0,*) = D(0,IGoodT)
      ;      DD(1,*) = D(1,IGoodT)
      ;      DD(2,*) = D(2,IGoodT)
      ;      DD(3,*) = D(3,IGoodT)
      ;      D       = DD
      ;      Tm      = TT(IGoodT)

      ; Now make the "Zero" one of two ways

      SIMPLE = 2  ; Leave as set

      IF SIMPLE EQ 1 THEN BEGIN ; Just use Min Value for Zero
        Z0min = 1000.0*MIN(D(0,*))
        Z1min = 1000.0*MIN(D(1,*))
        Z2min = 1000.0*MIN(D(2,*))
        Z3min = 1000.0*MIN(D(3,*))
      ENDIF

      IF SIMPLE EQ 2 THEN BEGIN; Use "PEAK" location of small counts as the Zero
        ; Determine the location of the "Low noise" and "High Noise" peaks

        Nbins = 501
        Min1  = 0.0
        Max1  = 5.0
        Binsize = (Max1 - Min1)/(Nbins-1) ; = 0.01

        Hplot = HISTOGRAM(D(0,*),BINSIZE=Binsize,MIN=Min1,MAX=Max1)
        INFO  = SIZE(Hplot)
        XX    = Min1+(Indgen(INFO(1)))*Binsize
        Result = MAX(Hplot(0:250),Max_Subscript)
        Result2 = MAX(Hplot(300:500),Max_Subscript2)
        PRINT,"Max_Subscript L/H 0:- ",Max_Subscript,XX(Max_Subscript),Max_Subscript2+300,XX(Max_Subscript2+300)
        Z0min = 1000.0*XX(Max_Subscript)

        Hplot = HISTOGRAM(D(1,*),BINSIZE=Binsize,MIN=Min1,MAX=Max1)
        INFO  = SIZE(Hplot)
        XX    = Min1+(Indgen(INFO(1)))*Binsize
        Result = MAX(Hplot(0:250),Max_Subscript)
        Result2 = MAX(Hplot(300:500),Max_Subscript2)
        PRINT,"Max_Subscript L/H 1:- ",Max_Subscript,XX(Max_Subscript),Max_Subscript2+300,XX(Max_Subscript2+300)
        Z1min = 1000.0*XX(Max_Subscript)

        Hplot = HISTOGRAM(D(2,*),BINSIZE=Binsize,MIN=Min1,MAX=Max1)
        INFO  = SIZE(Hplot)
        XX    = Min1+(Indgen(INFO(1)))*Binsize
        Result = MAX(Hplot(0:250),Max_Subscript)
        Result2 = MAX(Hplot(300:500),Max_Subscript2)
        PRINT,"Max_Subscript L/H 2:- ",Max_Subscript,XX(Max_Subscript),Max_Subscript2+300,XX(Max_Subscript2+300)
        Z2min = 1000.0*XX(Max_Subscript)

        Hplot = HISTOGRAM(D(3,*),BINSIZE=Binsize,MIN=Min1,MAX=Max1)
        INFO  = SIZE(Hplot)
        XX    = Min1+(Indgen(INFO(1)))*Binsize
        Result = MAX(Hplot(0:250),Max_Subscript)
        Result2 = MAX(Hplot(300:500),Max_Subscript2)
        PRINT,"Max_Subscript L/H 3:- ",Max_Subscript,XX(Max_Subscript),Max_Subscript2+300,XX(Max_Subscript2+300)
        Z3min = 1000.0*XX(Max_Subscript)
      ENDIF

    ENDIF
  ENDIF
  Dat = D
  EE = E
END


FUNCTION file_lines, filename
  ;#############################################################################
  ;## Function file_lines ######################################################
  ;#############################################################################
  ; get number of lines in file
  OPENR, unit, filename, /GET_LUN
  str = ''
  count = 0ll
  WHILE ~ EOF(unit) DO BEGIN
    READF, unit, str
    count = count + 1
  ENDWHILE
  FREE_LUN, unit
  RETURN, count
END

PRO Xray_002
;
; This simplified version of the LEXI IDL plotting program creates most of the plots as before
; In routine Read_File, change PATH to location of the data files, otherwise you will have to 
; navigate to them.
; Starting at line 966, comment out the ones you do not need.
; No warranties implied, feel free to make changes, just change the file name.
; D. Chornay 5/17/2022
;
READ_FILE,Filename,D,Tm,Z0min,Z1min,Z2min,Z3min,Events
PRINT,SIZE(D)
PRINT,SIZE(Tm)
PRINT,"Events ",Events
PRINT,Z0min,Z1min,Z2min,Z3min

n0Z = Z0min/1000.0
n1Z = Z1min/1000.0
n2Z = Z2min/1000.0
n3Z = Z3min/1000.0

; Corretcted 10/12/21
X0_raw = D(0,*) ; Wide Strip LHS      Ver 5 Anode Board J1
X1_raw = D(2,*) ; Wide Strip RHS      Ver 5 Anode Board J3
Y0_raw = D(3,*) ; Wedge Pointing Up   Ver 5 Anode Board J4
Y1_raw = D(1,*) ; Wedge Pointing Down Ver 5 Anode Board J2

X0 = X0_raw -n0Z    ; LEXI Remove offsets..
X1 = X1_raw -n2Z    ;
Y0 = Y0_raw -n3Z
Y1 = Y1_raw -n1Z

XP0 =  X1/(X0+X1)  ; eqn for X Pos, Strips  All the data
YP0 =  Y1/(Y0+Y1)  ; eqn for Y Pos, Wedges


PHD = (X0 + X1 + Y0 + Y1)
TMPIDX = WHERE(PHD GT 3.0)
Acc_Time = Tm(Events-1)-Tm(Tmpidx(0))
PRINT,"***********************************"
PRINT,"First PHD >3.0  "+STRING(Tm(Tmpidx(0)))
PRINT,"Accumulate Time At HV  "+STRING(Acc_Time)
PRINT,"***********************************"

XI = WHERE((PHD GE 5.0) AND (PHD LE 6.0))

XI_SIZE = SIZE(XI,/N_ELEMENTS)  ; These fit the criterea
PRINT,"XI_SIZE ",XI_SIZE
Percent = 100.0*XI_SIZE/Events
STR_XI_SIZE = STRTRIM(STRING(XI_SIZE),2)
STR_Percent = STRTRIM(STRING(Percent),2)
STR_Events  = STRTRIM(STRING(Events),2)
PRINT,"STR_XI_SIZE ",STR_XI_SIZE
PRINT,"STR_Percent ",STR_Percent
PRINT,"STR_Events ",STR_Events


PLOT_Counts_Time,Filename,Tm,Phd

Nbins = 512 ; change to 512 1024 2048 etc for higher res
PLOT_Pulse_Height_Dist,Filename,PHD,NBINS,D

Nbins = 512
PLOT_Contour_All,Filename,Nbins,XP0,YP0

Nbins = 512
Loglin = 1
PLOT_Contour_Panels,Filename,PHD,Xp0,Yp0,Nbins,Acc_Time,Loglin

Nbins = 512
Loglin = 1  ; 0 - Lin plots
PLOT_Scatter_Histogram,Filename,Nbins,X0,X1,Y0,Y1,Loglin

Nbins = 512
Loglin = 1
PLOT_Scatter_Histograms_other, Filename,Nbins,X0_raw,X1_Raw,Y0_raw,Y1_Raw,Loglin

END